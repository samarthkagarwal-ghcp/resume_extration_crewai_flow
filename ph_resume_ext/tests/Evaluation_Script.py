import os
import json
from tkinter.font import names
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score
from pydantic import BaseModel
from crewai.flow import Flow, start, listen

class EvalState(BaseModel):
    processed_resume_paths: list = []
    golden_resume_paths: list = []

class ResumeEvalFlow(Flow[EvalState]):
    processed_resume = r"C:\Users\samar\OneDrive\Documents\CrewAI\ph_resume_ext\src\ph_resume_ext\resume\processed"
    golden_resume = r"C:\Users\samar\OneDrive\Documents\CrewAI\ph_resume_ext\src\ph_resume_ext\resume\Golden_Records"


    def evaluate_field(self, pred, truth):
        return int(pred.strip().lower() == truth.strip().lower())

    def evaluate_skills(self, pred, truth):
        pred_set = set([s.lower() for s in pred])
        truth_set = set([s.lower() for s in truth])
        tp = len(pred_set & truth_set)
        fp = len(pred_set - truth_set)
        fn = len(truth_set - pred_set)

        precision = tp / (tp+fp) if tp+fp else 0
        recall = tp / (tp+fn) if tp+fn else 0
        f1 = 2*precision*recall/(precision+recall) if precision+recall else 0
        return precision, recall, f1


    @start()
    def load_processed(self):
        """Load processed resumes into state"""
        self.state.processed_resume_paths = [
            os.path.join(self.processed_resume, f)
            for f in os.listdir(self.processed_resume)
            if f.endswith(".json")
        ]
        return self.state.processed_resume_paths

    @listen("load_processed")
    def load_golden(self, _):
        """Load golden resumes into state"""
        self.state.golden_resume_paths = [
            os.path.join(self.golden_resume, f)
            for f in os.listdir(self.golden_resume)
            if f.endswith(".json")
        ]
        return self.state.golden_resume_paths

    @listen("load_golden")
    def evaluate(self, _):
        """Evaluate processed vs golden records"""
        # build golden dict
        golden_data = {}
        for gfile in self.state.golden_resume_paths:
            name = os.path.splitext(os.path.basename(gfile))[0]
            with open(gfile, "r", encoding="utf-8") as f:
                golden_data[name] = json.load(f)

        summary = []

        for pfile in self.state.processed_resume_paths:
            name = os.path.splitext(os.path.basename(pfile))[0]
            with open(pfile, "r", encoding="utf-8") as f:
                pred = json.load(f)

            truth = golden_data.get(name)
            if not truth:
                continue
            
            def get_field(d, *names):
                for name in names:
                    for k in d.keys():
                        if k.lower() == name.lower():
                            return d[k]
                return ""

            name_acc = self.evaluate_field(get_field(pred, "First_Name"), get_field(truth, "First_Name"))
            lname_acc = self.evaluate_field(get_field(pred, "Last_Name"), get_field(truth, "Last_Name"))
            email_acc = self.evaluate_field(get_field(pred, "Email_Address", "email_address"), get_field(truth, "Email_Address", "email_address"))
            p, r, f1 = self.evaluate_skills(get_field(pred, "Skills", "skills", []), get_field(truth, "Skills", "skills", []))

            summary.append({
                "resume": name,
                "first_name_acc": name_acc,
                "last_name_acc": lname_acc,
                "email_acc": email_acc,
                "skills_precision": p,
                "skills_recall": r,
                "skills_f1": f1
            })

        df = pd.DataFrame(summary)
        print("\n📊 Evaluation Results:\n", df)
        print("\nOverall F1 (skills):", df["skills_f1"].mean())
        output_csv = os.path.join(self.processed_resume, "evaluation_results.csv")
        df.to_csv(output_csv, index=False, encoding="utf-8")
        return df

def kickoff():
    Resume_Eval_Flow = ResumeEvalFlow()
    Resume_Eval_Flow.kickoff()


def plot():
    Resume_Eval_Flow = ResumeEvalFlow()
    Resume_Eval_Flow.plot()

if __name__ == "__main__":
    kickoff()