from flask import escape, current_app


@current_app.template_filter()
def format_number(num):
    if int(num) == num:
        return int(num)
    return num

# @current_app.context_processor
# def utility_processor():
#     return dict(escape=escape)
