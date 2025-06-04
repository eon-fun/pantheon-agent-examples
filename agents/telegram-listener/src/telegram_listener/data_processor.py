import asyncio
import enum
import os
import sys
from datetime import datetime, timedelta

from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient, models
from telethon import TelegramClient, events
from telethon.errors import ChatAdminRequiredError, UserAdminInvalidError, UserIdInvalidError
from telethon.tl.types import Message

from .schemas import QdrantPayload, TelegramMessageData, TelegramUser

QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant.qdrant.svc.cluster.local")
QDRANT_PORT = os.getenv("QDRANT_PORT", "6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

QDRANT_URL = f"http://{QDRANT_HOST}:{QDRANT_PORT}"

EMBEDDING_MODEL = "text-embedding-3-large"
OLD_QDRANT_COLLECTION_NAME = "telegram_messages"
KNOWLEDGE_BASE_COLLECTION_NAME = "telegram_knowledge_base"
EMBEDDING_DIM = 3072
OPENAI_MODEL = "gpt-4.1"

openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=60)


class MessageCategory(enum.Enum):
    SPAM = "SPAM"
    PROJECT_QUESTION = "PROJECT_QUESTION"
    OFF_TOPIC = "OFF_TOPIC"
    UNCATEGORIZED = "UNCATEGORIZED"


class MessageClassificationResult(BaseModel):
    category: MessageCategory
    reasoning: str = Field(description="Brief reasoning for the classification.")


class QueryExpansionResult(BaseModel):
    expanded_query: str


class FinalAnswerResult(BaseModel):
    answer: str


def initialize_qdrant():
    """Ensures the Qdrant collections exist. Raises exception on failure."""
    print("DEBUG: Attempting to initialize Qdrant...", file=sys.stderr)
    print(f"INFO: Initializing Qdrant connection to {QDRANT_URL}...")
    try:
        collections_response = qdrant_client.get_collections()
        existing_collections = [col.name for col in collections_response.collections]

        if OLD_QDRANT_COLLECTION_NAME not in existing_collections:
            print(f"INFO: Collection '{OLD_QDRANT_COLLECTION_NAME}' not found. Creating...")
            qdrant_client.create_collection(
                collection_name=OLD_QDRANT_COLLECTION_NAME,
                vectors_config=models.VectorParams(size=EMBEDDING_DIM, distance=models.Distance.COSINE),
            )
            print(f"INFO: Qdrant collection '{OLD_QDRANT_COLLECTION_NAME}' created.")
        else:
            print(f"INFO: Qdrant collection '{OLD_QDRANT_COLLECTION_NAME}' already exists.")

        if KNOWLEDGE_BASE_COLLECTION_NAME not in existing_collections:
            print(f"INFO: Collection '{KNOWLEDGE_BASE_COLLECTION_NAME}' not found. Creating...")
            qdrant_client.create_collection(
                collection_name=KNOWLEDGE_BASE_COLLECTION_NAME,
                vectors_config=models.VectorParams(size=EMBEDDING_DIM, distance=models.Distance.COSINE),
            )
            print(f"INFO: Qdrant collection '{KNOWLEDGE_BASE_COLLECTION_NAME}' created.")
        else:
            print(f"INFO: Qdrant collection '{KNOWLEDGE_BASE_COLLECTION_NAME}' already exists.")

        print("DEBUG: Qdrant initialized successfully.", file=sys.stderr)
    except Exception as e:
        print(f"DEBUG: Failed to initialize Qdrant: {e}", file=sys.stderr)
        print(f"ERROR: Failed to initialize Qdrant: {e}", file=sys.stderr)
        raise


async def get_embedding(text: str) -> list[float] | None:
    """Generates text embedding using OpenAI API."""
    if not text or not isinstance(text, str) or not text.strip():
        print("DEBUG: Skipping embedding for empty or non-string input.")
        return None

    try:
        print(f"DEBUG: Requesting embedding for text (first 50 chars): '{text[:50]}...' using {EMBEDDING_MODEL}")
        response = await openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=[text],
        )
        embedding = response.data[0].embedding
        print(f"DEBUG: Received embedding of dimension {len(embedding)}.")
        return embedding
    except Exception as e:
        print(f"ERROR: Failed to get embedding: {e}", file=sys.stderr)
        return None


def save_embedding_to_qdrant(collection_name: str, qdrant_point_id: int, embedding: list[float], payload: dict):
    if not embedding:
        print(
            f"DEBUG: No embedding provided for Qdrant point ID {qdrant_point_id} in {collection_name}. Skipping Qdrant save."
        )
        return

    try:
        qdrant_client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=qdrant_point_id,
                    vector=embedding,
                    payload=payload,
                )
            ],
            wait=False,
        )
        print(
            f"INFO: Embedding for message with Qdrant ID {qdrant_point_id} saved/updated in Qdrant collection {collection_name}."
        )
    except Exception as e:
        print(
            f"ERROR: Failed to save embedding for Qdrant ID {qdrant_point_id} to Qdrant collection {collection_name}: {e}",
            file=sys.stderr,
        )


async def send_telegram_message(
    client: TelegramClient, chat_id: int, message_text: str, reply_to_message_id: int | None = None
):
    """Sends a message to a Telegram chat, optionally replying to a specific message."""
    try:
        log_message = f"INFO: Attempting to send message to chat {chat_id}"
        if reply_to_message_id:
            log_message += f" (replying to message ID {reply_to_message_id})"
        log_message += f": '{message_text[:100]}...'"
        print(log_message)
        await client.send_message(entity=chat_id, message=message_text, reply_to=reply_to_message_id)
        print(f"INFO: Message successfully sent to chat {chat_id}.")
    except Exception as e:
        print(f"ERROR: Failed to send message to chat {chat_id}: {e}", file=sys.stderr)


async def classify_message_intent(user_message: str) -> MessageClassificationResult:
    """Classifies the user message into SPAM, PROJECT_QUESTION, or OFF_TOPIC."""
    system_prompt = """\
You are a message classification assistant for a Telegram bot operating in a chat about the Pantheon (EON) project.
Pantheon (EON) is a distributed, modular AI multi-agent ecosystem for creating scalable, composable, and self-evolving AI systems.
Key aspects of Pantheon include: Components (Tools, Agents, Projects), Dual-Layer Knowledge Architecture (Shared Memory, Private Memory), Orchestrator, Marketplace, $EON token.

Your task is to classify the user's message into one of three categories:
1. SPAM:
   - Advertisements of any kind (other products, services, crypto coins, etc.).
   - Abusive language, insults, or hate speech directed at anyone or the Pantheon project.
   - Repetitive, meaningless messages.
   - Links to clearly malicious or irrelevant websites.
2. PROJECT_QUESTION:
   - Direct questions about Pantheon (EON) features, components (Tools, Agents, Projects), $EON token, roadmap, technology.
   - Requests for documentation or help related to using Pantheon.
   - Discussions about developing with or using Pantheon.
   - Expressions of interest or requests for more information specifically about Pantheon.
3. OFF_TOPIC:
   - General greetings (e.g., "Hello", "How are you?").
   - Questions or comments completely unrelated to the Pantheon (EON) project or AI development in general (e.g., "What's the weather?", "News about sports").
   - Messages that are not SPAM but also clearly not a PROJECT_QUESTION.

Provide your classification and a brief reasoning.
"""
    try:
        completion = await openai_client.beta.chat.completions.parse(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            response_format=MessageClassificationResult,
        )

        message_response = completion.choices[0].message
        if message_response.refusal:
            print(
                f"ERROR: Message classification refused by model. Refusal: {message_response.refusal}", file=sys.stderr
            )
            return MessageClassificationResult(
                category=MessageCategory.UNCATEGORIZED,
                reasoning=f"Model refused to classify: {message_response.refusal}",
            )

        parsed_result = message_response.parsed
        if isinstance(parsed_result, MessageClassificationResult):
            print(
                f"DEBUG: Message classification: {parsed_result.category.value}, Reasoning: '{parsed_result.reasoning}'"
            )
            return parsed_result
        print(
            f"ERROR: Message classification did not return the expected Pydantic model. Type: {type(parsed_result)}",
            file=sys.stderr,
        )
        return MessageClassificationResult(
            category=MessageCategory.UNCATEGORIZED,
            reasoning="Error in classification processing, unexpected response structure.",
        )
    except Exception as e:
        print(f"ERROR: Failed to perform message classification: {e}", file=sys.stderr)
        return MessageClassificationResult(
            category=MessageCategory.UNCATEGORIZED, reasoning=f"Exception during classification: {str(e)}"
        )


async def ban_user_for_24_hours(client: TelegramClient, chat_id: int, user_id: int):
    """Restricts a user from sending messages in the chat for 24 hours."""
    try:
        until_date = datetime.now() + timedelta(days=1)
        print(
            f"INFO: Attempting to restrict user {user_id} in chat {chat_id} from sending messages until {until_date}."
        )

        await client.edit_permissions(chat_id, user_id, until_date=until_date, send_messages=False)

        print(f"INFO: User {user_id} has been restricted from sending messages in chat {chat_id} for 24 hours.")
    except ChatAdminRequiredError:
        print(
            f"ERROR: Failed to ban user {user_id}. Bot lacks admin rights or ban permission in chat {chat_id}.",
            file=sys.stderr,
        )
    except UserAdminInvalidError:
        print(
            f"ERROR: Failed to ban user {user_id}. Cannot ban another admin or owner in chat {chat_id}.",
            file=sys.stderr,
        )
    except UserIdInvalidError:
        print(f"ERROR: Failed to ban user {user_id}. Invalid user ID provided for chat {chat_id}.", file=sys.stderr)
    except Exception as e:
        print(
            f"ERROR: An unexpected error occurred while trying to ban user {user_id} in chat {chat_id}: {e}",
            file=sys.stderr,
        )


async def expand_query(user_message: str) -> QueryExpansionResult:
    """Expands the user query using OpenAI structured output."""
    system_prompt = """\
You are a query expansion assistant. Your task is to take a user's question about the Pantheon (EON) project
and rephrase it or add context to make it more effective for a semantic search in a knowledge base.
Focus on keywords and concepts related to Pantheon (EON) such as:
AI agents, tools, projects, distributed AI, modular AI, self-evolving systems, Shared Memory, Private Memory,
Qdrant, Orchestrator, Marketplace, $EON token, AI development, AI monetization, AI solutions.

Original query: {user_message}

Expand the query to be more descriptive and specific for information retrieval.
For example:
User: "Tell me about agents"
Expanded: "Detailed explanation of AI Agents in the Pantheon (EON) ecosystem, including their lifecycle, integration with tools and memory systems."

User: "What is $EON?"
Expanded: "Information about the $EON token in the Pantheon (EON) project, its utility, tokenomics, and role in the ecosystem."
"""
    try:
        completion = await openai_client.beta.chat.completions.parse(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt.format(user_message=user_message)},
                {"role": "user", "content": user_message},
            ],
            response_format=QueryExpansionResult,
        )

        message_response = completion.choices[0].message
        if message_response.refusal:
            print(f"ERROR: Query expansion refused by model. Refusal: {message_response.refusal}", file=sys.stderr)
            return QueryExpansionResult(expanded_query=user_message)

        parsed_result = message_response.parsed
        if isinstance(parsed_result, QueryExpansionResult):
            print(f"DEBUG: Query expansion result: expanded_query='{parsed_result.expanded_query}'")
            return parsed_result
        print(
            f"ERROR: Query expansion did not return the expected Pydantic model. Type: {type(parsed_result)}",
            file=sys.stderr,
        )
        return QueryExpansionResult(expanded_query=user_message)
    except Exception as e:
        print(f"ERROR: Failed to expand query: {e}", file=sys.stderr)
        return QueryExpansionResult(expanded_query=user_message)


async def search_knowledge_base(query_embedding: list[float], top_k: int = 5) -> list[str]:
    """Searches the knowledge base for relevant text chunks."""
    if not query_embedding:
        print("DEBUG: No query embedding provided for knowledge base search.")
        return []
    try:
        search_results = qdrant_client.search(
            collection_name=KNOWLEDGE_BASE_COLLECTION_NAME,
            query_vector=query_embedding,
            limit=top_k,
            with_payload=True,
        )
        contexts = [hit.payload.get("text", "") for hit in search_results if hit.payload and hit.payload.get("text")]
        contexts = [ctx for ctx in contexts if ctx.strip()]
        print(f"DEBUG: Found {len(contexts)} relevant contexts from knowledge base.")
        return contexts
    except Exception as e:
        print(f"ERROR: Failed to search knowledge base: {e}", file=sys.stderr)
        return []


async def generate_final_answer(user_message: str, contexts: list[str]) -> FinalAnswerResult:
    """Generates a final answer using OpenAI structured output, based on user message and contexts."""
    context_str = "\n\n".join(f"Context {i + 1}:\n{ctx}" for i, ctx in enumerate(contexts))
    if not contexts:
        context_str = "No relevant context found in the knowledge base."

    system_prompt = f"""\
You are a helpful AI assistant for the Pantheon (EON) project.
Your goal is to answer the user's question based on the provided context from the Pantheon (EON) knowledge base.
If the context is insufficient or doesn't directly answer the question, clearly state that and try to provide a general answer if possible,
or suggest what kind of information might be helpful.
Do not make up information not present in the context. Be concise and helpful.

User's question: {user_message}

Relevant context from the knowledge base:
---
{context_str}
---

Based on the user's question and the provided context, generate a helpful answer.
"""
    try:
        completion = await openai_client.beta.chat.completions.parse(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            response_format=FinalAnswerResult,
        )

        message_response = completion.choices[0].message
        if message_response.refusal:
            print(
                f"ERROR: Final answer generation refused by model. Refusal: {message_response.refusal}", file=sys.stderr
            )
            return FinalAnswerResult(
                answer=f"I am unable to provide an answer due to a model refusal: {message_response.refusal}"
            )

        parsed_result = message_response.parsed
        if isinstance(parsed_result, FinalAnswerResult):
            print(f"DEBUG: Final answer generation result: answer='{parsed_result.answer[:100]}...'")
            return parsed_result
        print(
            f"ERROR: Final answer generation did not return the expected Pydantic model. Type: {type(parsed_result)}",
            file=sys.stderr,
        )
        return FinalAnswerResult(answer="I encountered an issue while formulating my response. Please try again.")
    except Exception as e:
        print(f"ERROR: Failed to generate final answer: {e}", file=sys.stderr)
        return FinalAnswerResult(answer=f"I am unable to answer at this moment due to an error: {str(e)}")


async def process_new_message(event: events.NewMessage.Event, telegram_client: TelegramClient):
    message: Message = event.message
    raw_msg_dict = message.to_dict()
    user_id = message.sender_id
    chat_id = event.chat_id

    if not message.text or not user_id:
        print(f"DEBUG: Skipping message {message.id}: No text content or sender ID.")
        return

    print(
        f"INFO: Processing message {message.id} from chat {chat_id} by user {user_id}. Text: '{message.text[:50]}...'"
    )

    sender_data = TelegramUser(
        id=user_id,
        is_bot=getattr(message.sender, "bot", False),
        first_name=getattr(message.sender, "first_name", None),
        last_name=getattr(message.sender, "last_name", None),
        username=getattr(message.sender, "username", None),
    )
    message_data = TelegramMessageData(
        message_id=message.id,
        chat_id=chat_id,
        sender=sender_data,
        text=message.text,
        timestamp=message.date,
        raw_message=raw_msg_dict,
    )
    original_message_embedding = await get_embedding(message_data.text)
    if original_message_embedding:
        qdrant_payload_original = QdrantPayload(
            text=message_data.text,
            chat_id=message_data.chat_id,
            user_id=message_data.sender.id,
            username=message_data.sender.username,
            message_timestamp=message_data.timestamp,
        ).model_dump(exclude_none=True)
        save_embedding_to_qdrant(
            collection_name=OLD_QDRANT_COLLECTION_NAME,
            qdrant_point_id=message_data.message_id,
            embedding=original_message_embedding,
            payload=qdrant_payload_original,
        )

    print(f"DEBUG: [{message.id}] Classifying message intent...")
    classification_result = await classify_message_intent(message.text)

    if classification_result.category == MessageCategory.SPAM:
        print(
            f"INFO: [{message.id}] Message classified as SPAM. Reasoning: {classification_result.reasoning}. Attempting to ban user {user_id}."
        )
        await ban_user_for_24_hours(telegram_client, chat_id, user_id)
        return

    if classification_result.category == MessageCategory.OFF_TOPIC:
        print(
            f"INFO: [{message.id}] Message classified as OFF_TOPIC. Reasoning: {classification_result.reasoning}. No action taken."
        )
        return

    if classification_result.category == MessageCategory.UNCATEGORIZED:
        print(
            f"WARN: [{message.id}] Message could not be categorized. Reasoning: {classification_result.reasoning}. No action taken."
        )
        return

    if classification_result.category == MessageCategory.PROJECT_QUESTION:
        print(
            f"DEBUG: [{message.id}] Message is a PROJECT_QUESTION. Reasoning: {classification_result.reasoning}. Proceeding with answer generation."
        )

        print(f"DEBUG: [{message.id}] Expanding query...")
        query_expansion_result = await expand_query(message.text)
        expanded_query = query_expansion_result.expanded_query
        print(f"DEBUG: [{message.id}] Expanded query: '{expanded_query}'")

        print(f"DEBUG: [{message.id}] Getting embedding for expanded query...")
        expanded_query_embedding = await get_embedding(expanded_query)

        if not expanded_query_embedding:
            if original_message_embedding:
                print(
                    f"WARN: [{message.id}] Failed to get embedding for expanded query. Using original message embedding as fallback."
                )
                expanded_query_embedding = original_message_embedding
            else:
                print(
                    f"ERROR: [{message.id}] No embedding available for search (neither original nor expanded). Cannot proceed."
                )
                fallback_answer = "I had trouble processing your request to search our knowledge base. Could you please try rephrasing?"
                await send_telegram_message(telegram_client, chat_id, fallback_answer, reply_to_message_id=message.id)
                return

        print(f"DEBUG: [{message.id}] Searching knowledge base with embedding for query: '{expanded_query[:50]}...'")
        contexts = await search_knowledge_base(expanded_query_embedding, top_k=5)
        if not contexts:
            print(f"INFO: [{message.id}] No relevant documents found in knowledge base for query: '{expanded_query}'.")
        else:
            print(f"DEBUG: [{message.id}] Retrieved {len(contexts)} context items for the query.")

        print(f"DEBUG: [{message.id}] Generating final answer...")
        final_answer_result = await generate_final_answer(message.text, contexts)
        answer_to_send = final_answer_result.answer

        if not answer_to_send:
            print(f"WARN: [{message.id}] Generated answer was empty. Sending a default response.")
            answer_to_send = "I found some information, but I'm having a bit of trouble formulating a clear answer right now. Could you perhaps ask in a different way?"

        print(f"DEBUG: [{message.id}] Sending final answer to user...")
        await send_telegram_message(telegram_client, chat_id, answer_to_send, reply_to_message_id=message.id)

        print(f"DEBUG: Finished processing message {message.id}.")
        return

    print(
        f"ERROR: [{message.id}] Unknown message category: {classification_result.category}. No action taken.",
        file=sys.stderr,
    )
    return


async def initialize_data_processing():
    print("DEBUG: Starting initialize_data_processing...", file=sys.stderr)
    print("INFO: Initializing data processing components...")

    try:
        print("DEBUG: Attempting initialize_qdrant (via to_thread)...", file=sys.stderr)
        await asyncio.to_thread(initialize_qdrant)
        print("DEBUG: initialize_qdrant (via to_thread) completed.", file=sys.stderr)
    except Exception as e:
        print(f"DEBUG: Qdrant initialization failed critically: {e}", file=sys.stderr)
        print(f"CRITICAL: Qdrant initialization failed, which is critical: {e}", file=sys.stderr)
        raise

    print("DEBUG: initialize_data_processing completed (or Qdrant failed critically).", file=sys.stderr)
    print("INFO: Data processing components initialization attempt complete.")
