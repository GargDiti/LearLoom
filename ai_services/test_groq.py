from services.groq_services import explain_topic


topic = "Node.js File Paths"

content = """
Node.js provides the path module for working with
file and directory paths. The path.join() method joins
multiple path segments together and normalizes the result.
"""


answer = explain_topic(
    topic,
    content
)

print("\nAI Tutor Response:\n")
print(answer)