# news_ddd/schema.py
import graphene
import news.graphql.schema as news_schema
import media.schema as media_schema


class Query(
    news_schema.Query,
    media_schema.MediaQuery,
    graphene.ObjectType
):
    """Main GraphQL Query - Combines all queries from different modules"""
    pass


class Mutation(
    news_schema.Mutation,
    media_schema.MediaMutation,
    graphene.ObjectType
):
    """Main GraphQL Mutation - Combines all mutations from different modules"""
    pass


# Create schema
schema = graphene.Schema(query=Query, mutation=Mutation)

# Export for use in URLs
__all__ = ['schema']
