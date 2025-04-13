from dotenv import load_dotenv
from langgraphsetup.llm import model
from langgraphsetup.prompts.agentDefinition import agent_definition
from langgraphsetup.prompts.finalization import finalization_prompt
from typing import TypedDict, Annotated, List
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
import operator
from langgraph.graph import StateGraph, END
from sharedfunctions.print import print_success, print_bold
from langgraphsetup.llm import ChatOpenAI
from langgraphsetup.tools import select_tables, retrieve_schemas, generate_sql, run_sql
import time 
from langgraph.checkpoint.memory import MemorySaver



# load the environment variables
load_dotenv()

# generate a unique thread id by getting current time in unix
thread_id = str(int(time.time()))


# agent state and agent 
class AgentState(TypedDict):
    tables: list[str]
    schemas: list[str]
    sql: str
    sql_result: str
    message: str
    messages: Annotated[list[AnyMessage], operator.add] 
    final_response: str 
    
# agent  
class Agent:
    def __init__(self, model, tools, system=""):
        self.system = system
        graph = StateGraph(AgentState)
        graph.add_node("llm", self.call_openai)
        graph.add_node("action", self.take_action)
        graph.add_conditional_edges(
            "llm",
            self.exists_action,
            {True: "action", False: END}
        )
        graph.add_edge("action", "llm")
        graph.set_entry_point("llm")
        self.graph = graph.compile()
        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools)

    def exists_action(self, state: AgentState):
        result = state['messages'][-1]
        return len(result.tool_calls) > 0

    def call_openai(self, state: AgentState):
        messages = state['messages']
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        message = self.model.invoke(messages)
        return {'messages': [message]}

    def take_action(self, state: AgentState):
        tool_calls = state['messages'][-1].tool_calls
        
        # initiate the updated state dict 
        res = {}
        
        # initiate the tool message results
        message_results = []
            
        for t in tool_calls:
            print_success(f"\n\nBot is calling function: {t}\n\n")
            if not t['name'] in self.tools:      # check for bad tool name from LLM
                print("\n ....bad tool name....")
                result = "bad tool name, retry"  # instruct LLM to retry if bad
            else:
                tool_name = t['name']
                function_args = t["args"]                
                result = self.tools[tool_name].invoke(function_args)
                
                if tool_name != "retrieve_schemas":
                    print(f"\n\nFunction {tool_name} result: {result}\n\n")
                
                 # update the state dict with the result
                if tool_name == "select_tables":
                    res['tables'] = result
                
                elif tool_name == "retrieve_schemas":
                    res['schemas'] = result
                    
                elif tool_name == "generate_sql":
                    res['sql'] = result
                
                elif tool_name == "run_sql":
                    res['sql_result'] = result
            
            message_results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
            
        res['messages'] = message_results
        
        print_success("Function call completed. Bot proceeding to the next step...")
        return res


# define tools 
tools = [
    select_tables,
    retrieve_schemas,
    generate_sql,
    run_sql
]

# question -> 1. 判斷表格； 2. 拿相應schema； 3. 生成sql； 4. 執行sql

# define the sql node 
def sql_node(state: AgentState): 
    print_bold("\n\nSQL agent bot is running...\n\n")

    sql_bot = Agent(model, tools)
    
    messages = [
        SystemMessage(content=agent_definition), 
        HumanMessage(content=state['message'])
    ]

    # response = model.with_structured_output(GeneralSupportOutput).invoke(messages)
    response = sql_bot.graph.invoke({"messages": messages})
    
    return response 


# define the finalizer node 
def finalizer_node(state: AgentState):
    print_bold("\n\nFinalization bot is finalizing...\n\n")
    
    print(f"final agent state: {state}")
    
    finalization_bot = Agent(model, [])
    
    message = state.get("message") or "" 
    sql_result = state.get("sql_result") or ""
    tables = state.get("tables") or ""
    sql = state.get("sql") or ""   
    
    information_passed_down = f"""
    sql_result: {sql_result};
    message: {message};
    sql: {sql};
    tables: {tables}; 
    """
    
    messages = [
        SystemMessage(
            content=finalization_prompt.format(information_passed_down=information_passed_down)
        ),
        HumanMessage(content=message)
    ]
    
    
    response = finalization_bot.graph.invoke({"messages": messages})
    content = response['messages'][-1].content
    
    return {
        "final_response": content
    }
    
# build the graph and add nodes 
builder = StateGraph(AgentState)
builder.add_node("sql_generator", sql_node)
builder.add_node("finalizer", finalizer_node)
builder.set_entry_point("sql_generator")
builder.add_edge("sql_generator", "finalizer")



# add memory and complie graph
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)



# run the agent
def run_graph(message): 
    response = graph.invoke(
        {"message": message},
        config={
            "configurable": {"thread_id": thread_id}
        }
    )
    
    if "tables" in response:
        print(f"\n\nFinal response tables: {response['tables']}\n\n")
        
    if "sql_result" in response:
        print(f"\n\nFinal response sql_result: {response['sql_result']}\n\n")

    return response

