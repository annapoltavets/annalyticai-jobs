from typing import List, Optional
from enum import Enum
from pydantic import BaseModel
from spec import TitleEnum

class ExperienceLevel(str, Enum):
    JUNIOR = "JUNIOR"
    MIDDLE = "MIDDLE"
    SENIOR = "SENIOR"
    LEAD = "LEAD"

from enum import Enum

class ProgrammingLanguage(str, Enum):
    C = "C"
    CPP = "C++"
    CSHARP = "C#"
    JAVA = "Java"
    KOTLIN = "Kotlin"
    SCALA = "Scala"
    GO = "Go"                # aka Golang
    RUST = "Rust"
    PYTHON = "Python"
    RUBY = "Ruby"
    JAVASCRIPT = "JavaScript"
    TYPESCRIPT = "TypeScript"
    PHP = "PHP"
    SWIFT = "Swift"
    OBJECTIVE_C = "Objective-C"
    PERL = "Perl"
    LUA = "Lua"
    DART = "Dart"
    GROOVY = "Groovy"
    HASKELL = "Haskell"
    ERLANG = "Erlang"
    ELIXIR = "Elixir"
    R = "R"
    JULIA = "Julia"
    MATLAB = "MATLAB"
    ADA = "Ada"
    CLOJURE = "Clojure"
    FSHARP = "F#"
    VISUAL_BASIC = "Visual Basic" #scripting or VB.NET
    SQL = "SQL"  # any of sql dialects, e.g. T-SQL, PL/SQL, MySQL, PostgreSQL
    TCL = "Tcl"
    SCHEME = "Scheme"
    OCAML = "OCaml"
    SMALLTALK = "Smalltalk"
    COBOL = "COBOL"
    BASH_SH = "Bash/Sh"  # bash, sh, shell scripting, zsh, ksh, etc.
    ASSEMBLY = "Assembly"  # any assembly language, e.g. x86, ARM, MIPS, RISC-V, etc.
    VHDL = "VHDL"
    VERILOG = "Verilog"
    SYSTEMVERILOG = "SystemVerilog"


class ParsedJobDescription(BaseModel):
    job_description_id: str = None
    job_title: TitleEnum = TitleEnum.UNKNOWN
    experience_level: Optional[ExperienceLevel] = None

    required_technical_skills: List[str] = []   # essential skills and only required skills (avoid nice to have) or type of work that person has to be able to perform, e.g. "Python", "data pipelines", "React", "microservices", "fine-tuning", "project management", "sql queries", "query optimization"
    required_languages: List[ProgrammingLanguage] = []  # programming languages mentioned, e.g. "Python", "Java", "C++", "JavaScript", "Go", "Ruby", "R", "Scala", "Swift", "Kotlin", "PHP", "TypeScript"
    required_frameworks: List[str] = []         #frameworks, libraries, or tools, e.g. "Django", "React", "Angular", "Spring", "TensorFlow", "PyTorch", "Kubernetes", "Docker", "AWS", "GCP"
    required_datastores: List[str] = []        # databases, data warehouses, data lakes, e.g. "MySQL", "PostgreSQL", "MongoDB", "Redis", "Cassandra", "Elasticsearch", "Snowflake", "BigQuery", "Redshift", "Hadoop"
    required_tools: List[str] = []         # tools, e.g. "Git", "Jenkins", "Terraform", "Ansible", "Prometheus", "Grafana", "Splunk", "ELK Stack"
    required_cloud: List[str] = []           # cloud platforms, e.g. "AWS", "Azure", "GCP", "IBM Cloud", "Oracle Cloud"
    job_summary: str = []           # short summary of the job in 1-2 sentences
    is_government_job: Optional[bool] = False
