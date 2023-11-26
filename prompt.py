from langchain.prompts import ChatPromptTemplate

# Summary 
SUMMARY_PROMPT  = """{text}

------------

Using the above text, answer in short the following question: 

> {question}

------------
If the question cannot be answered using the text, you MUST simply summarize the text. Include all factual information, numbers, stats etc if available."""

summary_prompt = ChatPromptTemplate.from_template(SUMMARY_PROMPT)

# Search 
search_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "user",
            "Write 3 unique google search queries to search online that form an "
            "objective opinion from the following: {question}\n"
            "Your Output MUST BE IN PROPER JSON FORMAT as it will be read by a json.loads()"
            "You must respond with a list of strings in the following format: "
            '["query 1", "query 2", "query 3"].',
        ),
    ]
)

# Educate 
WRITER_SYSTEM_PROMPT = """You are a helpful AI tutor who is a master of all subjects dedicated to helping students learn and understand various topics in a friendly and focused manner. 
Your sole purpose is to provide well written and clear explanations about a given quest that empower students to grasp complex concepts. 
"""

EDUCATOR_PROMPT = """Information:
------------
{search_summary}
------------

Using the above information, answer the following question or topic: "{question}" in a detailed manor, citing your sources and elaborating on important points. -- \
Your explanation should focus on the answer to the question, should be well structured, informative, in depth, -
with facts and numbers if available and a minimum of 600 words. While your answer should be detailed, it should also be friendly 
and imformative to a wide audience. 

You should strive to write your explanations as long as necessary to cover all relevant and necessary information summarized. 
you MUST write your explanation with markdown syntax.
YOU MUST determine your own concrete and valid opinion based on the given information. Do NOT deter to general and meaningless commentary on the topic. 
Write all used source urls at the end of your explanation, and DO NOT add duplicated sources
Please do your best, this is going into a data sensitive application and is very important to my career
"""

educate_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", WRITER_SYSTEM_PROMPT),
        ("user", EDUCATOR_PROMPT),
    ]
)