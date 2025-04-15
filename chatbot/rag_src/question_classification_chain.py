from langchain_core.prompts import ChatPromptTemplate

from chatbot.rag_src.utils import llm

classification_template = """
You are a question classifier for a fashion e-commerce website. Classify the following question into one of the following categories:

1. Product Details
(Questions about specific products or product recommendations, such as about:
- Materials, fabrics, or product composition
- Available sizes, measurements, or fit
- Colors, styles, or design features
- Prices, discounts, or value
- Stock availability for specific items
- Seeking product recommendations or alternatives
- Product quality or durability
- Comparing different products
- Product care instructions
- Product specifications
- And any other questions related to product information)

2. Website Usage Guide
(Questions about how to use the website's features and functions, such as how to:
- Search for products or use filters
- Navigate categories and collections
- Add items to cart or manage cart
- Create account or log in
- Use account features
- Add items to favorites
- Check out or make payments
- Track orders
- Use website notifications
- Access user features like reviews or order history
- And any other questions related to website usage)

3. Both category 1 and 2
(Questions that fall under both categories 1 and 2
User can ask multiple questions or one question about product details and website usage)

4. Irrelevant Question
(Questions that are:
- Not related to fashion products
- Not related to website usage
- Spam or nonsensical queries
- Questions about unrelated topics
- General questions not specific to fashion or the website)

Be careful with tricky questions mentioning products but are actually about website usage or vice versa.

Question: {question}

Category (Respond only with the category number (1, 2, or 3). No explanation.):
"""

classification_prompt = ChatPromptTemplate.from_template(classification_template)
classification_chain = classification_prompt | llm

def classify_question(question):
    return classification_chain.invoke({"question": question}).content
#
# print(classify_question("Can I ask you a question?"))
# print(classify_question("How do I know if the dress I saved in favorites is still in stock?"))