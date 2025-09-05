from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import os
from ph_resume_ext.tools.doc_extractor_tool import ExtractTextTool
from ph_resume_ext.tools.Text_Cleaner import TextCleanerTool
from ph_resume_ext.tools.pdf_reader_tool import PDFReaderTool
from ph_resume_ext.type import Output_format

@CrewBase
class ResumeCrew:
    """Resume Crew"""

    # llm = LLM(
    #     # model=os.getenv("DEPLOYMENT_NAME"),
    #     # api_key=os.getenv("AZURE_API_KEY"),
    #     # api_base=os.getenv("AZURE_API_BASE"),
    #     # api_version=os.getenv("AZURE_API_VERSION"),
    #     model=f'google/{os.getenv("GEMINI_MODEL")}',
    #     api_key=os.getenv("GEMINI_API_KEY"),
    # )
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=r"ph_resume_ext\.env")

    llm = LLM(
        model=os.getenv("GEMINI_MODEL"),       # just "gemini-2.0-flash"
        api_key=os.getenv("GEMINI_API_KEY"),
        custom_llm_provider="gemini"           # ✅ tell LiteLLM which backend
    )

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def Extractor_Agent(self) -> Agent:
        return Agent(
            config=self.agents_config["Extractor_Agent"],  # type: ignore[index]
            verbose=True,
            llm=self.llm,
            tools=[PDFReaderTool()],
            temperature=0.2
        )
    
    @agent
    def Processor_Agent(self) -> Agent:
        return Agent(
            config=self.agents_config["Processor_Agent"],  # type: ignore[index]
            verbose=True,
            llm=self.llm,
            tools=[TextCleanerTool()],
            temperature=0.3,
            max_iter=3
        )

    @task
    def extract_content(self) -> Task:
        return Task(
            config=self.tasks_config["extract_content"],  # type: ignore[index]
            output_pydantic=Output_format,
            max_retries=3
        )
    
    def process_content(self) -> Task:
        return Task(
            config=self.tasks_config["process_content"],  # type: ignore[index]
            output_pydantic=Output_format
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Resume Crew"""

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=False,
            llm=self.llm,
        )
