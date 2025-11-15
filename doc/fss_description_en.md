FSS Document-based Neptune DB

🎯 Core Purpose

Digital Knowledge Transformation of IMO FSS Code - Converting the International Maritime Organization (IMO) Fire Safety Systems Code into a structured knowledge graph, enabling ship designers, inspectors, and regulatory authorities to utilize it in a searchable and interconnected format.

📊 Data Scale

Total Triples: 653

* Basic data unit of RDF: subject-predicate-object
* Represents one fact

CO2System rdf:type ExtinguishingSystem     ← 1 triple
CO2System rdfs:label "CO2 System"         ← 1 triple  
CO2System hasSpecification CO2_Capacity   ← 1 triple

Main Classes: 42 types

* Categories/classifications that group entities with similar characteristics

ExtinguishingSystem (class)
├── CO2System (instance)
├── NitrogenSystem (instance)  
├── HighExpansionFoamSystem (instance)
└── WaterSprayingSystem (instance)

Performance (class)
├── AlarmThreshold (instance)
├── FoamOperationDuration (instance)
└── H1_FoamDischarge (instance)

Chapter (class)
├── Chapter1 (instance)
├── Chapter2 (instance)
└── ... Chapter17 (instance)

🏗️ Schema Structure Design Principles

1. Hierarchical Document Structure Reflection

* 17 chapters each responsible for specific fire safety domains
* Direct mapping of document's physical structure to ontology

2. System-Centric Modeling

* Design centered around ExtinguishingSystem as the main axis
* Systematic connection of each system's components, performance, and requirements

3. Specification-Centric Information Structure

* Performance (38) - Specific performance values and criteria
* Capacity (16) - Capacity/output specifications
* Dimension (16) - Physical dimensions
* Temperature (4) - Temperature conditions
* All technical requirements structured as measurable values

🏗️ Core Class Hierarchy

* Performance (38) - Performance requirements
* Requirement (19) - General requirements
* Chapter (17) - FSS code chapters
* Capacity/Dimension (16 each) - Capacity/dimension specifications
* ExtinguishingSystem (11) - Fire suppression systems
* Component (9) - System components

📚 Chapter Class → 17 instances

Each chapter covers multiple systems:

* Chapter1 → ApplicationRule, ToxicMediumRule
* Chapter3 → FireFightersOutfit, EEBD
* Chapter5 → CO2System, NitrogenSystem
* Chapter6 → HighExpansionFoamSystem, LowExpansionFoamSystem, etc.

🔥 ExtinguishingSystem Class → 11 instances

Specific fire suppression systems:

* CO2System, NitrogenSystem
* HighExpansionFoamSystem, LowExpansionFoamSystem
* WaterSprayingSystem, WaterMistSystem
* DeckFoamSystem, HelideckFoamSystem

⚙️ Component Class → 9 instances

System components:

* SprinklerHead, SprinklerControlUnit
* SensingUnit, SamplingPipe
* InertGasGenerator, GasDistributionSystem

📋 Specification Class → Specific specifications

* Shore_Connection_Spec_Pressure = "1.0 N/mm²"
* DeckHeightSpec, CableRequirement, etc.

📊 Property Classification

1. Structural Relationship Properties (Object Properties)

* hasSpecification (84 times) - System/Component → Specification
* detailsSystem (31 times) - Chapter → System
* appliesTo (20 times) - System → Application target
* hasComponent (6 times) - System → Component
* partOf - Component → Parent system

2. Data Properties

* value (38 times) - Specific values (e.g., "1,200 l", "5 kg")
* requiredTime (19 times) - Time requirements (e.g., "30 min")
* hasDuration (8 times) - Duration
* hasDimension (7 times) - Dimension information
* hasTemperature (5 times) - Temperature values

3. Metadata Properties

* rdf:type (186 times) - Class classification (defines which class each instance belongs to)
* rdfs:label (29 times) - Labels/names
* rdfs:comment (114 times) - Descriptions/comments

System Structure Patterns:

* Chapter --detailsSystem→ ExtinguishingSystem
* ExtinguishingSystem --hasSpecification→ Performance
* ExtinguishingSystem --hasComponent→ Component
* ExtinguishingSystem --appliesTo→ ProtectedSpace

Specification Definition Patterns:

* Performance --value→ "Specific value"
* Performance --requiredTime→ "Time"
* Capacity --value→ "Capacity"
* Dimension --value→ "Dimension"