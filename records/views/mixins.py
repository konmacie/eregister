class PrevURLMixin:
    """
    Gets previous site url from GET parameters and adds to context data
    if it's present.
    """
    prev_url = None

    def dispatch(self, request, *args, **kwargs):
        self.prev_url = request.GET.get('prev', None)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        if self.prev_url:
            kwargs['prev'] = self.prev_url
        return super().get_context_data(**kwargs)
