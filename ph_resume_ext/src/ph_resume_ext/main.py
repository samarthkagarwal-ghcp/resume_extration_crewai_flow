import re
import json
import os
from pydantic import BaseModel
from ph_resume_ext.crews.resume_crew_pr.resume_crew import ResumeCrew
from crewai.flow import Flow, listen, start

os.environ['CREWAI_DISABLE_TELEMETRY'] = 'true'

class ResumeState(BaseModel):
    resume_paths: list = []

class ResumeFlow(Flow[ResumeState]):

    @start()
    def read_resume(self):
        """Find resume files and Store complete paths of each"""
        self.state.resume_paths = []
        resume = r"src\ph_resume_ext\resume\templates"

        if os.path.exists(resume):
            for file_name in os.listdir(resume):
                file_path = file_name
                # file_path = os.path.join(resume, file_name)
                if os.path.isfile(file_path):
                    self.state.resume_paths.append(file_name)
                else:
                    self.state.resume_paths.append(file_path)

    @listen(read_resume)
    def process_resumes(self):
        """Process each resume file found"""
        for resume_path in self.state.resume_paths:
            resume = r"src\ph_resume_ext\resume\templates"
            resume_processing_path = os.path.join(resume, resume_path)
            
            """Doc to PDF conversion"""
            format_type = os.path.splitext(resume_path)[1] 
            if format_type in ['.doc', '.docx']:
                from docx2pdf import convert
                pdf_path = os.path.join(resume, f"{os.path.splitext(resume_path)[0]}.pdf")
                convert(resume_processing_path, pdf_path)
                resume_processing_path = pdf_path

            print("Found resume:", resume_processing_path)
            result = (
                ResumeCrew()
                .crew()
                .kickoff(inputs={"file_path": resume_processing_path})
            )
            print("Resume processed", result.raw)

            def extract_json_from_markdown(text):
                """LLM's output in JSON structure are wrapped into JSON format by removing Markdown code blocks"""
                # Remove Markdown code block if present
                match = re.search(r"```(?:json)?\\s*([\\s\\S]*?)```", text, re.IGNORECASE)
                if match:
                    return match.group(1)
                # Try again with real newlines (not escaped)
                match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.IGNORECASE)
                if match:
                    return match.group(1)
                return text
            
            """Save output in JSON file format"""
            try:
                json_str = extract_json_from_markdown(result.raw)
                output = json.loads(json_str)
            except (json.JSONDecodeError, TypeError):
                print("Result was not JSON. Using raw text instead.")
                output = {"raw_text": result.raw}
            output_resume = r"src\ph_resume_ext\resume\processed"
            base_name = os.path.splitext(resume_path)[0] 
            output_path = os.path.join(output_resume, base_name + ".json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=4)


def kickoff():
    resume_flow = ResumeFlow()
    resume_flow.kickoff()


def plot():
    resume_flow = ResumeFlow()
    resume_flow.plot()

if __name__ == "__main__":
    kickoff()