from jinja2 import Template, Environment, FileSystemLoader


def render_recommendation_message(template_path, data):
    env = Environment(loader=FileSystemLoader('./templates'))

    template = env.get_template(template_path)

    template_data = {
        'pools_text': data['pools_text'],
        'best_pool': {
            'protocol_name': data['best_pool']['protocol_name'],
            'apy': data['best_pool']['apy'],
            'type': data['best_pool']['type'],
            'token_address': data['best_pool']['token_address'],
            'primary_address': data['best_pool']['primary_address']
        },
        'tokens_info': data['tokens_info']
    }

    rendered_text = template.render(**template_data)
    return rendered_text
