# Agentic Resume Extractor Crew

Welcome to the Agentic Resume Extractor Crew project, powered by [crewAI](https://crewai.com). This project automates resume extraction and processing using CrewAI agents. It converts Word resumes to PDF, extracts structured information using LLMs, and saves results in JSON format.

## Folder Structure

```
ph_resume_ext/
├── src/
│   └── ph_resume_ext/
│       ├── main.ipynb
│       ├── main.py
│       ├── crews/
│       │   └── resume_crew_pr/
│       │       ├── resume_crew.py
│       │       └── config/
│       └── resume/
│           ├── templates/
│           ├── processing/
│           └── processed/
├── tests/
│   ├── Evaluation_Script.ipynb
│   ├── Evaluation_Script.py
└── requirements.txt
```

## Features

- Converts `.doc`/`.docx` resumes to PDF
- Extracts resume data using CrewAI agents
- Saves extracted data as JSON
- Modular agent/task orchestration

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```sh
pip install uv
```

Next, navigate to your project directory and create virtual environment:
```sh
python -m venv .venv
.venv\Scripts\activate
```

Lock the dependencies and install them by using the CLI command:
```sh
crewai install
```

install the dependencies:
```sh
pip install -r requirements.txt
```

## Key Files

- `main.py` / `main.ipynb`: Main orchestration logic
- `resume_crew.py`: CrewAI agent definitions
- `resume/templates/`: Place your resume files here
- `resume/processing/`: Intermediate processed files
- `resume/processed/`: Final JSON outputs


### Customization

**Add your `GEMINI_MODEL` and `GEMINI_API_KEY` into the `.env` file**

- Created `src/ph_resume_ext/config/agents.yaml` to define agents
- Created `src/ph_resume_ext/config/tasks.yaml` to define tasks
- Created `src/ph_resume_ext/resume_crew.py` to add agent logic, tools and specific args

### Jupyter Notebook

You can run `src/ph_resume_ext/main.ipynb` for step-by-step execution and debugging.

### OR

### python file 
You can also run `src/ph_resume_ext/main.py` to execute in a single flow
    or 
    You can kickstart your flow and begin execution, run this from the root folder of your project:

    ```bash
    crewai run
    ```
    This command initializes the ph_resume_ext Flow as defined in your configuration.

## Troubleshooting

- Ensure `.venv` is activated before installing/running.
- If `docx2pdf` or other libraries are not found, reinstall them inside `.venv`.
- Check your working directory if file paths are not resolving.

## License

MIT License

