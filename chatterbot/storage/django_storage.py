from chatterbot.storage import StorageAdapter
from chatterbot import constants


class DjangoStorageAdapter(StorageAdapter):
    """
    Storage adapter that allows ChatterBot to interact with
    Django storage backends.
    """

    def __init__(self, **kwargs):
        super(DjangoStorageAdapter, self).__init__(**kwargs)

        self.adapter_supports_queries = False
        self.django_app_name = kwargs.get(
            'django_app_name',
            constants.DEFAULT_DJANGO_APP_NAME
        )

    def get_statement_model(self):
        from django.apps import apps
        return apps.get_model(self.django_app_name, 'Statement')

    def get_tag_model(self):
        from django.apps import apps
        return apps.get_model(self.django_app_name, 'Tag')

    def count(self):
        Statement = self.get_model('statement')
        return Statement.objects.count()

    def filter(self, **kwargs):
        """
        Returns a list of statements in the database
        that match the parameters specified.
        """
        Statement = self.get_model('statement')

        order_by = kwargs.pop('order_by', None)
        tags = kwargs.pop('tags', [])

        # Convert a single sting into a list if only one tag is provided
        if type(tags) == str:
            tags = [tags]

        if tags:
            kwargs['tags__name__in'] = tags

        statements = Statement.objects.filter(**kwargs)

        if order_by:
            statements = statements.order_by(*order_by)

        return statements

    def create(self, **kwargs):
        """
        Creates a new statement matching the keyword arguments specified.
        Returns the created statement.
        """
        Statement = self.get_model('statement')
        Tag = self.get_model('tag')

        tags = kwargs.pop('tags', [])

        if 'search_text' not in kwargs:
            kwargs['search_text'] = self.stemmer.stem(kwargs['text'])

        if 'search_in_response_to' not in kwargs:
            if kwargs.get('in_response_to'):
                kwargs['search_in_response_to'] = self.stemmer.stem(kwargs['in_response_to'])

        statement = Statement(**kwargs)

        statement.save()

        tags_to_add = []

        for _tag in tags:
            tag, _ = Tag.objects.get_or_create(name=_tag)
            tags_to_add.append(tag)

        statement.tags.add(*tags_to_add)

        return statement

    def create_many(self, statements):
        """
        Creates multiple statement entries.
        """
        Statement = self.get_model('statement')
        Tag = self.get_model('tag')

        tag_cache = {}

        for statement in statements:

            statement_model_object = Statement(
                text=statement.text,
                search_text=statement.search_text,
                conversation=statement.conversation,
                persona=statement.persona,
                in_response_to=statement.in_response_to,
                search_in_response_to=statement.search_in_response_to,
                created_at=statement.created_at
            )

            if not statement.search_text:
                statement_model_object.search_text = self.stemmer.stem(statement.text)

            if not statement.search_in_response_to and statement.in_response_to:
                statement_model_object.search_in_response_to = self.stemmer.stem(statement.in_response_to)

            statement_model_object.save()

            tags_to_add = []

            for tag_name in statement.tags:
                if tag_name in tag_cache:
                    tag = tag_cache[tag_name]
                else:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    tag_cache[tag_name] = tag
                tags_to_add.append(tag)

            statement_model_object.tags.add(*tags_to_add)

    def update(self, statement):
        """
        Update the provided statement.
        """
        Statement = self.get_model('statement')
        Tag = self.get_model('tag')

        if hasattr(statement, 'id'):
            statement.save()
        else:
            statement = Statement.objects.create(
                text=statement.text,
                search_text=self.stemmer.stem(statement.text),
                conversation=statement.conversation,
                in_response_to=statement.in_response_to,
                search_in_response_to=self.stemmer.stem(statement.in_response_to),
                created_at=statement.created_at
            )

        for _tag in statement.tags.all():
            tag, _ = Tag.objects.get_or_create(name=_tag)

            statement.tags.add(tag)

        return statement

    def get_random(self):
        """
        Returns a random statement from the database
        """
        Statement = self.get_model('statement')
        return Statement.objects.order_by('?').first()

    def remove(self, statement_text):
        """
        Removes the statement that matches the input text.
        Removes any responses from statements if the response text matches the
        input text.
        """
        Statement = self.get_model('statement')

        statements = Statement.objects.filter(text=statement_text)

        statements.delete()

    def drop(self):
        """
        Remove all data from the database.
        """
        Statement = self.get_model('statement')
        Tag = self.get_model('tag')

        Statement.objects.all().delete()
        Tag.objects.all().delete()

    def get_response_statements(self, page_size=1000):
        """
        Return only statements that are in response to another statement.
        A statement must exist which lists the closest matching statement in the
        in_response_to field. Otherwise, the logic adapter may find a closest
        matching statement that does not have a known response.
        """
        Statement = self.get_model('statement')

        total_statements = self.count()
        start = 0
        stop = min(page_size, total_statements)

        while stop <= total_statements:

            statements_with_responses = Statement.objects.filter(
                in_response_to__isnull=False
            )[start:stop].values_list('in_response_to', flat=True)

            start += page_size
            stop += page_size

            for statement in Statement.objects.exclude(
                persona__startswith='bot:'
            ).filter(
                text__in=statements_with_responses
            ):
                yield statement
