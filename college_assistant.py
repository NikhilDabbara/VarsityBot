import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
from typing import List
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
try:
    from langchain.agents import create_tool_calling_agent, AgentExecutor
except ImportError:
    from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_ollama import ChatOllama

# Get the model from the .env file
load_dotenv()
Model = os.getenv("Model", "qwen2.5:3b")

# Define Tools using @tool decorator

@tool
def attendance_calculator(total_classes: int, attended_classes: int) -> str:
    """Calculates attendance percentage and exam eligibility status.
    
    Args:
        total_classes: Total number of classes held.
        attended_classes: Number of classes attended.
    """
    if total_classes <= 0:
        return "Error: Total classes must be greater than 0."
    if attended_classes < 0:
        return "Error: Attended classes cannot be negative."
    if attended_classes > total_classes:
        return "Error: Attended classes cannot exceed total classes."
        
    percentage = (attended_classes / total_classes) * 100
    eligibility = "Eligible for Exam" if percentage >= 75.0 else "Not Eligible for Exam"
    return f"Attendance Percentage: {percentage:.2f}%. Status: {eligibility}."


@tool
def result_calculator(subject_marks: List[float]) -> str:
    """Calculates the average marks, grade, and pass/fail status for 5 subjects.
    
    Args:
        subject_marks: A list of exactly 5 numbers representing the marks of the subjects (e.g., [95, 90, 88, 91, 87]).
    """
    if not isinstance(subject_marks, list) or len(subject_marks) != 5:
        return "Error: Please provide marks for exactly 5 subjects as a list of numbers."
    
    for idx, mark in enumerate(subject_marks):
        try:
            val = float(mark)
            subject_marks[idx] = val
        except ValueError:
            return f"Error: All marks must be numbers. Invalid value: {mark}"
            
        if val < 0 or val > 100:
            return f"Error: Marks must be between 0 and 100. Invalid mark: {val}"
            
    average = sum(subject_marks) / 5.0
    
    if average >= 90:
        grade = "A"
    elif average >= 75:
        grade = "B"
    elif average >= 60:
        grade = "C"
    else:
        grade = "D"
        
    status = "Pass" if average >= 50.0 else "Fail"
    return f"Average Marks: {average:.2f}, Grade: {grade}, Status: {status}."


@tool
def fee_balance_calculator(total_course_fee: float, amount_paid: float) -> str:
    """Calculates the pending course fee amount.
    
    Args:
        total_course_fee: The total fee of the course.
        amount_paid: The amount of course fee already paid.
    """
    if total_course_fee < 0 or amount_paid < 0:
        return "Error: Fees cannot be negative values."
    pending = total_course_fee - amount_paid
    return f"Total Fee: ₹{total_course_fee:.2f}, Paid: ₹{amount_paid:.2f}, Pending Fee Amount: ₹{pending:.2f}."


@tool
def library_fine_calculator(delayed_days: int) -> str:
    """Calculates the library fine amount.
    
    Args:
        delayed_days: Number of days the book return is delayed.
    """
    if delayed_days < 0:
        return "Error: Delayed days cannot be negative."
    fine = 5 * delayed_days
    return f"Delayed Days: {delayed_days}, Fine Amount: ₹{fine}."


@tool
def hostel_fee_calculator(monthly_hostel_fee: float, number_of_months_stayed: int) -> str:
    """Calculates the total hostel fee based on monthly rent and stay duration.
    
    Args:
        monthly_hostel_fee: Monthly hostel fee rate.
        number_of_months_stayed: Number of months stayed in the hostel.
    """
    if monthly_hostel_fee < 0 or number_of_months_stayed < 0:
        return "Error: Fee and stay duration must be non-negative."
    total = monthly_hostel_fee * number_of_months_stayed
    return f"Monthly Fee: ₹{monthly_hostel_fee:.2f}, Months Stayed: {number_of_months_stayed}, Total Hostel Fee: ₹{total:.2f}."

# Define the System Prompt
SYSTEM_PROMPT = """You are a helpful and precise College Assistant AI. You have access to custom calculators to help students with their queries.
You must use the provided tools to answer student questions accurately.

CRITICAL RULE: You MUST invoke the appropriate tool for ALL calculations (attendance, grades, fee balances, library fines, and hostel fees). Do NOT calculate any results manually or make assumptions. Always call the corresponding tool first and base your response entirely on the tool's output.

Here are the rules you must enforce based on tool outputs:
1. Attendance Calculator:
   - Attendance >= 75% -> Eligible for Exam
   - Attendance < 75% -> Not Eligible for Exam
2. Result Calculator:
   - Grade boundaries:
     Average >= 90: Grade A
     75 <= Average < 90: Grade B
     60 <= Average < 75: Grade C
     Average < 60: Grade D
   - Pass Status: Pass if Average >= 50, otherwise Fail.
3. Fee Balance Calculator:
   - Pending Fee = Total Course Fee - Amount Paid.
4. Library Fine Calculator:
   - Calculates the library fine. The exact rate is configured inside the tool.
5. Hostel Fee Calculator:
   - Total Hostel Fee = Monthly Hostel Fee * Number of Months Stayed.

Please respond clearly and directly based on the tool's output.
"""

def main():
    print("=" * 60)
    print("         College Assistant Chatbot ({Model})         ")
    print("=" * 60)
    print("Initializing LangChain Ollama Agent...")

    try:
        # Initialize ChatOllama LLM (using qwen2.5:3b locally)
        # Bind the defined tools to the model
        llm = ChatOllama(model=Model, temperature=0.0)
        
        # Tools list
        tools = [
            attendance_calculator,
            result_calculator,
            fee_balance_calculator,
            library_fine_calculator,
            hostel_fee_calculator
        ]

        # Define the prompt template using messages format
        # In order to place system prompt in the chat history list dynamically:
        # We start chat_history with the SystemMessage.
        # So we specify MessagesPlaceholder(variable_name="chat_history") at the top.
        prompt = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create tool-calling agent
        agent = create_tool_calling_agent(llm, tools, prompt)

        # Create AgentExecutor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=6,
            max_execution_time=30,
        )

    except Exception as e:
        print(f"\nInitialization Error: {e}")
        print("Please verify that Ollama is running and langchain-ollama is installed.")
        sys.exit(1)

    # Maintain a chat history in memory. 
    # The system prompt is appended first to the chat history as requested.
    chat_history = [SystemMessage(content=SYSTEM_PROMPT)]

    print("\nInitialization complete! Type 'exit' or 'exxit' to stop.")
    print("-" * 60)
    
    MAX_TURNS = 6
    
    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if user_input.lower() in ["exit", "bye", "quit"]:
            print("Chatbot: Goodbye! Have a nice day!")
            break

        if not user_input:
            print("Please enter something")
            continue

        print("Chatbot thinking...")
        try:
            # Run the agent executor
            result = agent_executor.invoke({
                "input": user_input,
                "chat_history": chat_history
            })
            
            response = result.get("output", "No response generated.")
            print(f"\nChatbot: {response}\n" + "-" * 60)
            
            # Append user prompt and agent response to keep the chat history updated
            chat_history.append(HumanMessage(content=user_input))
            chat_history.append(AIMessage(content=response))
            if len(chat_history) > (MAX_TURNS * 2 + 1):  # +1 for system msg
                chat_history = [chat_history[0]] + chat_history[-(MAX_TURNS * 2):]

        except Exception as e:
            print(f"\nAn error occurred during execution: {e}")
            print("Make sure the Ollama service is running locally on port 11434.")
            print("-" * 60)

if __name__ == "__main__":
    main()
