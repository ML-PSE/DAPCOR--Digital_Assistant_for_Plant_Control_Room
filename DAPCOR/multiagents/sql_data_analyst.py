'''
The code in this script is adapted from the AI Data Science Team's (https://github.com/business-science/ai-data-science-team) SQL Data Analyst Agent.
The original code was shared under the MIT License which reads as follows:

Copyright (c) 2024 ai-data-science-team authors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Adapted by: Ankur Kumar @ ProcessIndustryAI LLC [January 2025]

'''

#%% import packages
import pandas as pd, json
from IPython.display import Markdown

import operator
from typing import TypedDict, Annotated, Sequence, Literal
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langgraph.types import Checkpointer
from langgraph.graph import START, END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command

from DAPCOR.templates import BaseAgent
from DAPCOR.agents import SQLDatabaseAgent, DataVisualizationAgent
from DAPCOR.utils.plotly import plotly_from_dict
from DAPCOR.utils.regex import remove_consecutive_duplicates, get_generic_summary

#%% class
class SQLDataAnalyst(BaseAgent):
    """
    SQLDataAnalyst is a multi-agent class that combines SQL database querying and data visualization capabilities.
    
    Parameters:
    -----------
    model:
        The language model to be used for the agents.
    sql_database_agent: SQLDatabaseAgent
        The SQL Database Agent.
    data_visualization_agent: DataVisualizationAgent
        The Data Visualization Agent.
        
    Methods:
    --------
    ainvoke_agent(user_instructions, **kwargs)
        Asynchronously invokes the SQL Data Analyst Multi-Agent with the given user instructions.
    invoke_agent(user_instructions, **kwargs)
        Invokes the SQL Data Analyst Multi-Agent with the given user instructions.
    get_data_sql()
        Returns the SQL data as a Pandas DataFrame.
    get_plotly_graph()
        Returns the Plotly graph as a Plotly object.
    get_sql_query_code(markdown=False)
        Returns the SQL query code as a string, optionally formatted as a Markdown code block.
    get_sql_database_function(markdown=False)
        Returns the SQL database function as a string, optionally formatted as a Markdown code block.
    get_data_visualization_function(markdown=False)
        Returns the data visualization function as a string, optionally formatted as a Markdown code block.
    """
    
    def __init__(
        self, 
        model, 
        sql_database_agent: SQLDatabaseAgent, 
        data_visualization_agent: DataVisualizationAgent,
        checkpointer: Checkpointer = None,
    ):
        self._params = {
            "model": model,
            "sql_database_agent": sql_database_agent,
            "data_visualization_agent": data_visualization_agent,
            "checkpointer": checkpointer,
        }
        self._compiled_graph = self._make_compiled_graph()
        self.response = None
    
    def _make_compiled_graph(self):
        """
        Create or rebuild the compiled graph for the SQL Data Analyst Multi-Agent.
        Running this method resets the response to None.
        """
        self.response = None
        return make_sql_data_analyst(
            model=self._params["model"],
            sql_database_agent=self._params["sql_database_agent"]._compiled_graph,
            data_visualization_agent=self._params["data_visualization_agent"]._compiled_graph,
            checkpointer=self._params["checkpointer"],
        )
    
    def update_params(self, **kwargs):
        """
        Updates the agent's parameters (e.g. model, sql_database_agent, etc.) 
        and rebuilds the compiled graph.
        """
        for k, v in kwargs.items():
            self._params[k] = v
        self._compiled_graph = self._make_compiled_graph()
        
    async def ainvoke_agent(self, user_instructions, max_retries:int=3, retry_count:int=0, **kwargs):
        """
        Asynchronosly nvokes the SQL Data Analyst Multi-Agent.
        
        Parameters:
        ----------
        user_instructions: str
            The user's instructions for the combined SQL and (optionally) Data Visualization agents.
        **kwargs:
            Additional keyword arguments to pass to the compiled graph's `ainvoke` method.
            
        Returns:
        -------
        None. The response is stored in the `response` attribute.
        
        Example:
        --------
        ``` python
        from langchain_openai import ChatOpenAI
        import sqlalchemy as sql
        from ai_data_science_team.multiagents import SQLDataAnalyst
        from ai_data_science_team.agents import SQLDatabaseAgent, DataVisualizationAgent
        
        llm = ChatOpenAI(model = "gpt-4o-mini")
        
        sql_engine = sql.create_engine("sqlite:///data/northwind.db")

        conn = sql_engine.connect()
        
        sql_data_analyst = SQLDataAnalyst(
            model = llm,
            sql_database_agent = SQLDatabaseAgent(
                model = llm,
                connection = conn,
                n_samples = 1,
            ),
            data_visualization_agent = DataVisualizationAgent(
                model = llm,
                n_samples = 10,
            )
        )
        
        sql_data_analyst.ainvoke_agent(
            user_instructions = "Make a plot of sales revenue by month by territory. Make a dropdown for the user to select the territory.",
        )
        
        sql_data_analyst.get_sql_query_code()
        
        sql_data_analyst.get_data_sql()
        
        sql_data_analyst.get_plotly_graph()
        ```
        """
        response = await self._compiled_graph.ainvoke({
            "user_instructions": user_instructions,
            "max_retries": max_retries,
            "retry_count": retry_count,
        }, **kwargs)
        
        if response.get("messages"):
            response["messages"] = remove_consecutive_duplicates(response["messages"])
        
        self.response = response
        
    def invoke_agent(self, user_instructions, max_retries:int=3, retry_count:int=0, **kwargs):
        """
        Invokes the SQL Data Analyst Multi-Agent.
        
        Parameters:
        ----------
        user_instructions: str
            The user's instructions for the combined SQL and (optionally) Data Visualization agents.
        max_retries (int): 
                Maximum retry attempts for cleaning.
        retry_count (int): 
            Current retry attempt.
        **kwargs:
            Additional keyword arguments to pass to the compiled graph's `invoke` method.
            
        Returns:
        -------
        None. The response is stored in the `response` attribute.
        
        Example:
        --------
        ``` python
        from langchain_openai import ChatOpenAI
        import sqlalchemy as sql
        from ai_data_science_team.multiagents import SQLDataAnalyst
        from ai_data_science_team.agents import SQLDatabaseAgent, DataVisualizationAgent
        
        llm = ChatOpenAI(model = "gpt-4o-mini")
        
        sql_engine = sql.create_engine("sqlite:///data/northwind.db")

        conn = sql_engine.connect()
        
        sql_data_analyst = SQLDataAnalyst(
            model = llm,
            sql_database_agent = SQLDatabaseAgent(
                model = llm,
                connection = conn,
                n_samples = 1,
            ),
            data_visualization_agent = DataVisualizationAgent(
                model = llm,
                n_samples = 10,
            )
        )
        
        sql_data_analyst.invoke_agent(
            user_instructions = "Make a plot of sales revenue by month by territory. Make a dropdown for the user to select the territory.",
        )
        
        sql_data_analyst.get_sql_query_code()
        
        sql_data_analyst.get_data_sql()
        
        sql_data_analyst.get_plotly_graph()
        ```
        """
        response = self._compiled_graph.invoke({
            "user_instructions": user_instructions,
            "max_retries": max_retries,
            "retry_count": retry_count,
        }, **kwargs)
        
        if response.get("messages"):
            response["messages"] = remove_consecutive_duplicates(response["messages"])
        
        self.response = response
        
        
    def get_data_sql(self):
        """
        Returns the SQL data as a Pandas DataFrame.
        """
        if self.response:
            if self.response.get("data_sql"):
                return pd.DataFrame(self.response.get("data_sql"))
    
    def get_plotly_graph(self):
        """
        Returns the Plotly graph as a Plotly object.
        """
        if self.response:
            if self.response.get("plotly_graph"):
                return plotly_from_dict(self.response.get("plotly_graph"))
    
    def get_sql_query_code(self, markdown=False):
        """
        Returns the SQL query code as a string.
        
        Parameters:
        ----------
        markdown: bool
            If True, returns the code as a Markdown code block for Jupyter (IPython).
            For streamlit, use `st.code()` instead.
        """
        if self.response:
            if self.response.get("sql_query_code"):
                if markdown:
                    return Markdown(f"```sql\n{self.response.get('sql_query_code')}\n```")
                return self.response.get("sql_query_code")
    
    def get_sql_database_function(self, markdown=False):
        """
        Returns the SQL database function as a string.
        
        Parameters:
        ----------
        markdown: bool
            If True, returns the function as a Markdown code block for Jupyter (IPython).
            For streamlit, use `st.code()` instead.
        """
        if self.response:
            if self.response.get("sql_database_function"):
                if markdown:
                    return Markdown(f"```python\n{self.response.get('sql_database_function')}\n```")
                return self.response.get("sql_database_function")
    
    def get_data_visualization_function(self, markdown=False):
        """
        Returns the data visualization function as a string.
        
        Parameters:
        ----------
        markdown: bool
            If True, returns the function as a Markdown code block for Jupyter (IPython).
            For streamlit, use `st.code()` instead.
        """
        if self.response:
            if self.response.get("data_visualization_function"):
                if markdown:
                    return Markdown(f"```python\n{self.response.get('data_visualization_function')}\n```")
                return self.response.get("data_visualization_function")
            
    def get_workflow_summary(self, markdown=False):
        """
        Returns a summary of the SQL Data Analyst workflow.
        
        Parameters:
        ----------
        markdown: bool
            If True, returns the summary as a Markdown-formatted string.
        """
        if self.response and self.get_response()['messages']:
            
            agents = [self.get_response()['messages'][i].role for i in range(len(self.get_response()['messages']))]
            
            agent_labels = []
            for i in range(len(agents)):
                agent_labels.append(f"- **Agent {i+1}:** {agents[i]}")
            
            # Construct header
            header = f"# SQL Data Analyst Workflow Summary Report\n\nThis agentic workflow contains {len(agents)} agents:\n\n" + "\n".join(agent_labels)
            
            reports = []
            for msg in self.get_response()['messages']:
                reports.append(get_generic_summary(json.loads(msg.content)))
                
            if markdown:
                return Markdown(header + "\n\n".join(reports))
            return "\n\n".join(reports)
    
    
#%% functions
def make_sql_data_analyst(
    model, 
    sql_database_agent: CompiledStateGraph,
    data_visualization_agent: CompiledStateGraph,
    checkpointer: Checkpointer = None
):
    """
    Creates a multi-agent system that takes in a SQL query and returns a plot or table.
    
    - Agent 1: SQL Database Agent made with `make_sql_database_agent()`
    - Agent 2: Data Visualization Agent made with `make_data_visualization_agent()`
    
    Parameters:
    ----------
    model: 
        The language model to be used for the agents.
    sql_database_agent: CompiledStateGraph
        The SQL Database Agent made with `make_sql_database_agent()`.
    data_visualization_agent: CompiledStateGraph
        The Data Visualization Agent made with `make_data_visualization_agent()`.
    checkpointer: Checkpointer (optional)
        The checkpointer to save the state of the multi-agent system.
        Default: None
        
    Returns:
    -------
    CompiledStateGraph
        The compiled multi-agent system.
    """
    
    llm = model

    class PrimaryState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], operator.add]    
        user_instructions: str
        sql_query_code: str
        sql_database_function: str
        data_sql: dict
        user_answer: str
        data_raw: dict
        plot_required: bool
        data_visualization_function: str
        plotly_graph: dict
        max_retries: int
        retry_count: int
        
    def route_to_visualization(state) -> Command[Literal["data_visualization_agent", "__end__"]]: 
        
        response = llm.invoke(f"Respond in 1 word ('plot' or 'table'). Is the user requesting a plot? If unknown, select 'table'. \n\n User Instructions:\n{state.get('user_instructions')}")
        
        if response.content == 'plot':
            plot_required = True
            goto="data_visualization_agent"
        else:
            plot_required = False
            goto="__end__"
        
        return Command(
            update={
                'data_raw': state.get("data_sql"),
                'plot_required': plot_required,
            },
            goto=goto
        )

    workflow = StateGraph(PrimaryState)

    workflow.add_node("sql_database_agent", sql_database_agent)
    workflow.add_node("route_to_visualization", route_to_visualization)
    workflow.add_node("data_visualization_agent", data_visualization_agent)

    workflow.add_edge(START, "sql_database_agent")
    workflow.add_edge("sql_database_agent", "route_to_visualization")
    workflow.add_edge("data_visualization_agent", END)

    app = workflow.compile(checkpointer=checkpointer)

    return app

