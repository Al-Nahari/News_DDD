# news_ddd/schema.py
import graphene
import news.graphql.schema as news_schema


class Query(
    news_schema.Query,
    graphene.ObjectType
):
    """Main GraphQL Query - Combines all queries from different modules"""
    pass


class Mutation(
    news_schema.Mutation,
    graphene.ObjectType
):
    """Main GraphQL Mutation - Combines all mutations from different modules"""
    pass


# Create schema
schema = graphene.Schema(query=Query, mutation=Mutation)

# Export for use in URLs
__all__ = ['schema']
