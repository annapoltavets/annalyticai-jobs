from enum import Enum


class SearchCategory(str, Enum):
    MANAGEMENT = 'project management'
    LEAD = 'lead'
    AI_ML = 'ai/ml'
    BACKEND = 'backend'
    BUSINESS_ANALYSIS = 'business analysis'
    CYBERSECURITY = 'cybersecurity'
    DATA = 'data'
    DEVOPS = 'devops'
    ENGINEER = 'engineer'
    FRONTEND = 'frontend'
    GAMES_DEVELOPMENT = 'games development'
    HARDWARE = 'hardware'

    MOBILE = 'mobile'
    QA = 'qa'
    UI_UX_DESIGN = 'ui/ux design'


class TitleEnum(str, Enum):
    PROJECT_MANAGER = "IT Project Manager"
    PRODUCT_OWNER = "Product Manager"

    MACHINE_LEARNING_ENGINEER = "ML Engineer"
    PROMPT_ENGINEER = "Prompt Engineer"
    COMPUTER_VISION_ENGINEER = "Computer Vision Engineer"
    ROBOTICS_ENGINEER = "Robotics Engineer"

    DATA_ENGINEER = "Data Engineer"
    BI_DEVELOPER = "BI Developer"
    DATABASE_ADMINISTRATOR = "Database Administrator"
    DATA_ARCHITECT = "Data Architect"

    SOFTWARE_ENGINEER = "Software Engineer"
    FULL_STACK_ENGINEER = "Full Stack Engineer"
    FRONTEND_ENGINEER = "Frontend Engineer"
    BACKEND_ENGINEER = "Backend Engineer"

    DEVOPS_ENGINEER = "DevOps Engineer"
    BLOCKCHAIN_DEVELOPER = "Blockchain Developer"
    GAME_DEVELOPER = "Game Developer"
    MOBILE_DEVELOPER = "Mobile Developer"
    HARDWARE_ENGINEER = "Hardware Engineer"
    EMBEDDED_FIRMWARE_ENGINEER = "Embedded Engineer"

    LEAD_PRINCIPAL_ENGINEER = "Lead/Principal Engineer"
    SOLUTION_ARCHITECT = "Solution Architect"
    SOFTWARE_ARCHITECT = "Software Architect"


    SECURITY_ENGINEER = "Security Engineer"
    SECURITY_ANALYST = "Security Analyst"
    PENETRATION_TESTER = "Penetration Tester"
    SECURITY_ARCHITECT = "Security Architect"

    DATA_SCIENTIST = "Data Scientist"
    BUSINESS_ANALYST = "Business Analyst"
    TECHNICAL_WRITER = "Technical Writer"

    UI_UX_DESIGNER = "UI/UX Designer"
    GRAPHIC_DESIGNER = "Graphic Designer"
    SYSTEM_DESIGNER = "System Designer"


    AUTOMATION_TEST_ENGINEER = "Automation Test Engineer"
    MANUAL_TESTER = "Manual Tester"
    QA_LEAD = "QA Lead"

    UNKNOWN = "Unknown"

SPEC = {
    SearchCategory.MANAGEMENT.value: {
        'reference_titles': [
            TitleEnum.PROJECT_MANAGER.value,
            TitleEnum.PRODUCT_OWNER.value
        ],
        "search": [
            'agile project manager',
            'it project manager',
            'project coordinator',
            'project lead',
            'project manager',
            'product owner',
            'product manager',
            'scrum master'
        ],
        "rules": [
            "Prefer IT Project Manager if (pmp|agile|scrum|jira|timeline|budget).",
            "Prefer Product Manager if (backlog ownership|roadmap|prioritization|grooming|user stories|acceptance criteria|kpi|user research) even if PM terms appear.",
            "If both PM and Product signals exist: choose PM when (schedule|budget|risk|raid) dominate; else choose Product Manager."
        ]
    },

    SearchCategory.LEAD.value: {
        'reference_titles': [
            TitleEnum.LEAD_PRINCIPAL_ENGINEER.value,
            TitleEnum.SOLUTION_ARCHITECT.value,
            TitleEnum.SOFTWARE_ARCHITECT.value
        ],
        "search": [
            'enterprise architect',
            'lead engineer',
            'principal engineer',
            'software architect',
            'solutions architect',
            'staff engineer',
            'team lead',
            'tech lead'
        ],
        "rules": [
            "Prefer Lead/Principal Engineer if (principal|staff|tech lead|lead engineer) AND (system design|architecture) AND (cross-team|org-wide standards|mentorship|strategy).",
            "Prefer Solution Architect if (customer workshops|discovery|demos|pre-sales|rfp|sow|estimation|tco|sizing|landing zone|reference architecture|well-architected).",
            "Prefer Software Architect if (nfrs|scalability|reliability|security|performance) AND (microservices|ddd|api design|messaging|caching) AND (adr|rfc|c4|uml|design docs).",
            "If both Solution and Software Architect signals exist: choose Solution Architect when customer-facing or cost/TCO words are present; otherwise Software Architect.",
            "If 'enterprise architect' appears: map to Solution Architect when cloud reference architectures + stakeholder workshops are present; otherwise Software Architect when internal platform/application design + NFRs dominate.",
            "If both Lead/Principal and Architect signals exist: choose Lead/Principal Engineer when cross-team IC leadership dominates; choose Software Architect for internal design/NFR ownership; choose Solution Architect for customer-facing design/presales."
        ]
    },

    SearchCategory.HARDWARE.value: {
        'reference_titles': [TitleEnum.HARDWARE_ENGINEER.value, TitleEnum.ROBOTICS_ENGINEER.value, TitleEnum.EMBEDDED_FIRMWARE_ENGINEER.value],
        'search': [
            'embedded software engineer',
            'embedded systems developer',
            'hardware design engineer',
            'fpga developer',
            'iot developer',
            'robotics engineer'
        ],
        'rules': [
            '''Prefer Hardware Engineer when hardware is primary: PCB/bring-up/lab; high-speed I/O + SI/PI (PCIe/DDR/USB/SerDes); 
            FPGA/RTL (Verilog/VHDL + Vivado/Quartus + timing closure); 
            or server/RF/test domains (BMC/IPMI/UEFI, ATE/EVT-DVT-PVT, EMI/EMC/HFSS/ADS).''',
            '''Prefer Hardware Engineer for embedded platform bring-up and low-level firmware tightly coupled to boards: 
            Yocto/Device Tree/U-Boot/drivers/BSP, RTOS/bootloader, MCU buses (I²C/SPI/UART/CAN), with clear board ownership.''',
            '''Prefer Robotics Engineer when ROS/ROS2 + MoveIt/OMPL and controls (kinematics/planning/navigation) 
            or a full autonomy stack (perception + planning + control) on physical robots.''',
            '''Prefer Embedded Engineer when embedded or firmware mentioned in title or description without strong hardware/robotics signals.'''
        ]
    },

    SearchCategory.AI_ML.value: {
        'reference_titles': [
            TitleEnum.MACHINE_LEARNING_ENGINEER.value,
            TitleEnum.DATA_SCIENTIST.value,
            TitleEnum.PROMPT_ENGINEER.value,
            TitleEnum.COMPUTER_VISION_ENGINEER.value
        ],
        'search': [
            'ai agents engineer', 'ai prompt engineer', 'ai/ml researcher',
            'computer vision engineer', 'data analyst', 'data scientist',
            'deep learning engineer', 'gen ai engineer', 'llm engineer',
            'machine learning engineer', 'mlops engineer', 'nlp engineer'
        ],
        'rules': [
            'Prefer ML Engineer when model training/serving + MLOps pipelines (mlflow|kserve|sagemaker|vertex) + monitoring/drift appear.',
            'Prefer Data Scientist when experimentation/A-B testing/metrics, notebooks, and modeling (sklearn|xgboost|stats) dominate with light deployment.',
            'Prefer Prompt Engineer when LLM + (RAG|retrievers|vector DB) + prompt eval/guardrails + LangChain/LlamaIndex appear.',
            'Prefer Computer Vision Engineer when (OpenCV|torchvision|object detection|segmentation|camera calibration|SLAM) dominate.',
            'Prefer DevOps Engineer if cluster ops/IaC/k8s/GitOps dominate with minimal ML.',
            'Prefer Data Engineer if ETL/ELT/warehousing/dbt/streaming dominate over modeling/serving.'
        ]
    },

    SearchCategory.BACKEND.value: {
        'reference_titles': [
            TitleEnum.BACKEND_ENGINEER.value,
            TitleEnum.SOFTWARE_ENGINEER.value,
            TitleEnum.FULL_STACK_ENGINEER.value,
            TitleEnum.BLOCKCHAIN_DEVELOPER.value
        ],
        'search': [
            '.net developer', 'c or c++ developer', 'c# developer', 'backend developer',
            'blockchain developer', 'java engineer',
            'php developer', 'python developer', 'rust developer', 'scala developer'
        ],
        'rules': [
            'Prefer Backend Engineer when APIs (REST/gRPC), services, databases, and messaging (Kafka/Rabbit/SQS) dominate.',
            'Prefer Full Stack Engineer if strong SPA/UI framework + backend/API + DB signals co-occur.',
            'Prefer Software Engineer if language + algorithms/data structures + CI/CD are present without clear web/service stack.',
            'Prefer Blockchain Developer when Solidity/EVM/Web3/Rust+Anchor/Substrate/Cosmos SDK signals dominate.'
        ]
    },

    SearchCategory.BUSINESS_ANALYSIS.value: {
        'reference_titles': [
            TitleEnum.BUSINESS_ANALYST.value,
            TitleEnum.PRODUCT_OWNER.value,
            TitleEnum.SYSTEM_DESIGNER.value,
            TitleEnum.TECHNICAL_WRITER.value
        ],
        'search': [
            'business analyst', 'systems analyst', 'technical writer', 'requirements analyst'
        ],
        'rules': [
            'Prefer Business Analyst when requirements/user stories/acceptance criteria + process mapping (as-is/to-be/BPMN) dominate.',
            'Prefer Product Manager (Owner) when backlog ownership, prioritization, roadmap, and KPIs/OKRs are central.',
            'Prefer System Designer when integration patterns + API contracts + NFRs/constraints are emphasized.',
            'Prefer Technical Writer when docs-as-code + API/SDK docs + diagrams are core deliverables.',
            'Prefer IT Project Manager if schedule/budget/risk/status reporting dominate.'
        ]
    },

    SearchCategory.CYBERSECURITY.value: {
        'reference_titles': [
            TitleEnum.SECURITY_ENGINEER.value,
            TitleEnum.SECURITY_ANALYST.value,
            TitleEnum.PENETRATION_TESTER.value,
            TitleEnum.SECURITY_ARCHITECT.value
        ],
        'search': [
            'application security engineer', 'cryptographer', 'cybersecurity analyst',
            'ethical hacker', 'incident response analyst', 'information security specialist',
            'malware analyst', 'penetration tester', 'security architect',
            'security operations center (soc) analyst'
        ],
        'rules': [
            'Prefer Security Analyst when SIEM + incident response + EDR/XDR + SOAR operations dominate.',
            'Prefer Penetration Tester when adversary emulation + Kali/Burp/Metasploit + OWASP/AD exploitation dominate.',
            'Prefer Security Engineer when hardening, vulnerability/risk remediation, IAM/KMS/secrets, and DevSecOps/policy-as-code dominate.',
            'Prefer Security Architect when frameworks/controls/reference architectures, zero-trust, and cloud security architectures dominate.',
            'Prefer DevOps Engineer if pipelines/k8s/IaC dominate with minimal security ownership.'
        ]
    },

    SearchCategory.DATA.value: {
        'reference_titles': [
            TitleEnum.DATA_ENGINEER.value,
            TitleEnum.BI_DEVELOPER.value,
            TitleEnum.DATABASE_ADMINISTRATOR.value,
            TitleEnum.DATA_ARCHITECT.value,
            TitleEnum.DATA_SCIENTIST.value
        ],
        'search': [
            'bi business intelligence developer', 'big data architect', 'big data engineer',
            'data architect', 'data engineer', 'database administrator or dba',
            'database developer', 'etl developer', 'sql developer',
            'warehouse architect', 'warehouse engineer'
        ],
        'rules': [
            'Prefer Data Engineer when ETL/ELT/pipelines + orchestration (Airflow/Dagster/Prefect) + Spark/Databricks appear + data lake modeling/data warehouse modeling.',
            "Prefer BI Developer when Power BI/Tableau/Cognos/Informatica/SSIS/SSRS/Pentaho are present even if generic 'data engineer' appears.",
            'Prefer Data Architect when governance/lineage/modeling + platform/reference architectures dominate.',
            'Prefer Database Administrator when backup/recovery/replication/HA + tuning/indexing + engine-specific tooling appear.',
            'Prefer Data Scientist when modeling/evaluation dominate over pipelines/BI.',
            'Prefer ML Engineer when model training/serving + MLOps pipelines (mlflow|kserve|sagemaker|vertex) + monitoring/drift appear.',
            'Prefer Data Engineer if PL/SQL or Oracle developer or T-SQL developer signals dominate over modeling/analysis.'
        ]
    },

    SearchCategory.DEVOPS.value: {
        'reference_titles': [
            TitleEnum.DEVOPS_ENGINEER.value,
            TitleEnum.SECURITY_ENGINEER.value,
            TitleEnum.SOFTWARE_ENGINEER.value,
            TitleEnum.SOLUTION_ARCHITECT.value
        ],
        'search': [
            'cloud engineer', 'cloud security engineer', 'cloud solutions architect',
            'devops engineer', 'infrastructure as code specialist',
            'kubernetes engineer', 'site reliability engineer'
        ],
        'rules': [
            'Prefer DevOps Engineer when IaC (Terraform/CloudFormation/Pulumi) + CI/CD + containers/k8s + monitoring (Prometheus/Grafana/Otel) dominate.',
            'Prefer Security Engineer when WAF/GuardDuty/Security Hub, IAM/KMS/secrets, policy-as-code, or supply chain (SAST/DAST/SCA/SBOM) dominate.',
            'Prefer Software Engineer when internal developer platform/tooling/APIs and application code dominate over infra ops.',
            'Prefer Solution Architect when customer workshops, TCO/estimation, and cloud landing zones/reference architectures dominate.'
        ]
    },

    SearchCategory.ENGINEER.value: {
        'reference_titles': [
            TitleEnum.SOFTWARE_ENGINEER.value,
            TitleEnum.FULL_STACK_ENGINEER.value,
            TitleEnum.BACKEND_ENGINEER.value,
            TitleEnum.FRONTEND_ENGINEER.value
        ],
        'search': [
            'api developer', 'firmware engineer', 'full stack developer',
            'pre-sales engineer', 'software developer', 'software engineer', 'tools developer'
        ],
        'rules': [
            'Prefer Software Engineer when strong language + algorithms/data structures + CI/CD are present without clear FE/BE tilt.',
            'Prefer Backend Engineer when APIs/services/databases/messaging dominate.',
            'Prefer Frontend Engineer when SPA frameworks (React/Angular/Vue) + UI patterns dominate with minimal backend.',
            'Prefer Full Stack Engineer when FE framework + backend/API + database all appear.',
            'Prefer Solution Architect if pre-sales/workshops/RFP/TCO dominate over building.'
        ]
    },

    SearchCategory.FRONTEND.value: {
        'reference_titles': [
            TitleEnum.FRONTEND_ENGINEER.value,
            TitleEnum.FULL_STACK_ENGINEER.value,
            TitleEnum.SOFTWARE_ENGINEER.value,
            TitleEnum.UI_UX_DESIGNER.value
        ],
        'search': [
            'angular developer', 'frontend developer', 'javascript developer',
            'node.js developer', 'react developer', 'typescript developer', 'web developer'
        ],
        'rules': [
            'Prefer Frontend Engineer when SPA frameworks (React/Angular/Vue/Svelte) + state mgmt + testing (Jest/Cypress/RTL) dominate.',
            'Prefer Full Stack Engineer if backend/API/database signals are substantial alongside FE stack.',
            'Prefer UI/UX Designer if research, wireframes/prototypes, design systems, and usability testing dominate over coding.',
            'Prefer Software Engineer if FE is light and general coding patterns/algorithms dominate.'
        ]
    },

    SearchCategory.GAMES_DEVELOPMENT.value: {
        'reference_titles': [
            TitleEnum.GAME_DEVELOPER.value,
            TitleEnum.MOBILE_DEVELOPER.value,
            TitleEnum.SOFTWARE_ENGINEER.value
        ],
        'search': [
            'game developer', 'game designer', 'game engine programmer', 'unity unreal developer', 'vr ar developer'
        ],
        'rules': [
            'Prefer Game Developer when Unity/Unreal/Godot + gameplay/rendering/physics/networking systems appear.',
            'Boost Game Developer when rendering/shaders + GPU profiling tools (RenderDoc/Nsight/PIX) are present.',
            'Prefer Mobile Developer if iOS/Android frameworks dominate without engine/game systems.',
            'Prefer Software Engineer if generic app dev with no game engine signals.'
        ]
    },

    SearchCategory.MOBILE.value: {
        'reference_titles': [
            TitleEnum.MOBILE_DEVELOPER.value,
            TitleEnum.GAME_DEVELOPER.value,
            TitleEnum.SOFTWARE_ENGINEER.value
        ],
        'search': [
            'android developer', 'ios developer', 'mobile app developer', 'swift developer', 'kotlin developer'
        ],
        'rules': [
            'Prefer Mobile Developer when platform language + modern UI toolkit + store/release tooling co-occur (e.g., Swift+SwiftUI+TestFlight or Kotlin+Compose+Play Console).',
            'Boost Mobile Developer when DI + MVVM/MVI + offline/persistence (Room/CoreData/Realm) appear.',
            'Prefer Game Developer if Unity/Unreal/gameplay/rendering dominate.',
            'Prefer Software Engineer if mobile signals are weak and general coding dominates.'
        ]
    },

    SearchCategory.QA.value: {
        'reference_titles': [
            TitleEnum.AUTOMATION_TEST_ENGINEER.value,
            TitleEnum.MANUAL_TESTER.value,
            TitleEnum.QA_LEAD.value
        ],
        'search': [
            'automation test engineer', 'manual tester', 'performance tester',
            'qa engineer', 'qa lead', 'test manager', 'sdet'
        ],
        'rules': [
            'Prefer Automation Test Engineer (SDET) when Selenium/Cypress/Playwright/Robot + coding + CI/CD are present.',
            'Prefer QA Lead when strategy/planning/coordination with dev/pm + stakeholder acceptance/UAT leadership are emphasized.',
            'Prefer Manual Tester when manual testing + test plans/cases/acceptance tests dominate without automation frameworks.',
            'Prefer Automation Test Engineer if both manual and automation signals exist with active framework ownership.'
        ]
    },

    SearchCategory.UI_UX_DESIGN.value: {
        'reference_titles': [
            TitleEnum.UI_UX_DESIGNER.value,
            TitleEnum.GRAPHIC_DESIGNER.value,
            TitleEnum.SYSTEM_DESIGNER.value,
            TitleEnum.FRONTEND_ENGINEER.value
        ],
        'search': [
            'design system specialist', 'graphic designer', 'interaction designer',
            'motion designer', 'ui/ux designer', 'ux researcher'
        ],
        'rules': [
            'Prefer UI/UX Designer when research + prototyping + usability + design systems are present.',
            'Prefer Graphic Designer when branding/visual/motion assets dominate without UX research/flows.',
            'Prefer System Designer when integration patterns, API contracts, and NFRs/constraints dominate.',
            'Prefer Frontend Engineer if bulk of work is coding components rather than designing them.'
        ]
    }
}
