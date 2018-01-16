@fridashboardapp.after_request
def response_minify(response):
    from htmlmin.main import minify
    if response.content_type == u'text/html; charset=utf-8':
        response.set_data(
            minify(response.get_data(as_text=True))
        )
        return response
    return response
