from fastapi import HTTPException
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from openai import OpenAI

from app.config import logger
from app.constants import API_KEY, MODEL_NAME
from app.dao.mongo import get_mongo_connection

async def process_image_with_gpt4o(base_encoded_image: str):
    try:
        client = OpenAI(api_key=API_KEY)

        logger.info("Getting data from OpenAI")

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "You are an expert in grocery bill analysis. Extract the following information "
                                "from the attached grocery bill and return a dict object in this format:\n\n"
                                "{"
                                '"bill_date": <date str in YYYY-MM-DD format>,'
                                '"bill_total": <int>,'
                                '"items": ['
                                '  {'
                                '    "item_name": <str>,'
                                '    "category": <str>,'
                                '    "price": <int>,'
                                '    "quantity": <int>'
                                '  },'
                                '  {'
                                '    "item_name": <str>,'
                                '    "category": <str>,'
                                '    "price": <int>,'
                                '    "quantity": <int>'
                                '  }'
                                ']'
                                "}\n\n"
                                "Please ensure all fields are accurate and the bill total is the sum of all item "
                                "prices.\nMake sure to return only the dict of key-value pairs in the response with no "
                                "preceding or following text like ```json."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base_encoded_image}"},
                        },
                    ]
                }
            ],
            temperature=0
        )

        json_data = response.choices[0].message.content
        logger.info(f"Received response: {json_data}")
        try:
            structured_data = eval(json_data)
            return structured_data
        except Exception as e:
            logger.error(f"Failed to parse JSON: {str(e)}")
            raise ValueError(f"Failed to parse JSON: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing image with GPT-4o: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing image with GPT-4o: {str(e)}")


async def get_results_from_query(query: str, user_id: int):
    logger.info("Fetching results from user query")
    llm = ChatOpenAI(
        model=MODEL_NAME,
        temperature=0,
        api_key=API_KEY
    )
    prompt = PromptTemplate(
        input_variables=["query"],
        template=(
            "You are a MongoDB query expert. Convert the following user query into a MongoDB query which can be passed"
            " to the .find() method of pymongo library. Make sure to return only the MongoDB Query. "
            "Don't use any extra text like ```json in the response."
            "User Query: {query}\n"
            "MongoDB Collection Schema:\n"
            "{{"
            "  '_id': 'ObjectId', 'user_id': 'int', 'bill_date': 'str in YYYY-MM-DD format', 'bill_total': 'int', "
            "  'items': [{{'item_name': 'str', 'category': 'str', 'price': 'int', 'quantity': 'int'}}], "
            "  'timestamp': 'timestamp'"
            "}}\n"
            "MongoDB Query:"
        )
    )
    chain = prompt | llm | StrOutputParser()

    logger.info("Sending request to LLM")
    # Generate the MongoDB query using LangChain
    generated_query = chain.invoke({"query": f"User ID: {user_id}\nQuery: " + query})

    # Log and validate the generated query
    logger.info(f"Generated MongoDB Query: {generated_query}")
    try:
        mongo_query = eval(generated_query)  # Safely parse the query
        if not isinstance(mongo_query, dict):
            logger.error("Generated query is not a valid MongoDB query.")
            raise ValueError("Generated query is not a valid MongoDB query.")
    except Exception as e:
        logger.error(f"Error parsing MongoDB query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error parsing MongoDB query: {str(e)}")

    db = get_mongo_connection()
    collection = db["groceries"]

    # Execute the query on the groceries collection
    results = list(collection.find(mongo_query, {"_id": 0}))

    return results
