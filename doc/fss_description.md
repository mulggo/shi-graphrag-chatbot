FSS 문서 기반 Neptune DB

🎯 핵심 목적

IMO FSS Code의 디지털 지식화 - 국제해사기구(IMO)의 화재 안전 시스템 코드를 구조화된 지식 그래프로 변환하여, 선박 설계자, 검사관, 규제 당국이 검색 가능하고 연결된 형태로 활용할 수 있게 함.

📊 데이터 규모

총 트리플: 653개

* RDF의 기본 데이터 단위: 주어-술어-목적어
* 하나의 사실(fact)을 표현

CO2System rdf:type ExtinguishingSystem     ← 1개 트리플
CO2System rdfs:label "CO2 System"         ← 1개 트리플  
CO2System hasSpecification CO2_Capacity   ← 1개 트리플

주요 클래스: 42개 타입

* 비슷한 특성을 가진 엔티티들을 묶는 카테고리/분류

ExtinguishingSystem (클래스)
├── CO2System (인스턴스)
├── NitrogenSystem (인스턴스)  
├── HighExpansionFoamSystem (인스턴스)
└── WaterSprayingSystem (인스턴스)

Performance (클래스)
├── AlarmThreshold (인스턴스)
├── FoamOperationDuration (인스턴스)
└── H1_FoamDischarge (인스턴스)

Chapter (클래스)
├── Chapter1 (인스턴스)
├── Chapter2 (인스턴스)
└── ... Chapter17 (인스턴스)

🏗️ 스키마 구조 설계 원리

1. 계층적 문서 구조 반영

* 17개 챕터가 각각 특정 화재 안전 영역을 담당
* 문서의 물리적 구조를 온톨로지로 그대로 매핑

2. 시스템 중심 모델링

* ExtinguishingSystem을 중심축으로 하는 설계
* 각 시스템의 구성요소, 성능, 요구사항을 체계적으로 연결

3. 사양 중심 정보 구조

* Performance (38개) - 구체적 성능 수치와 기준
* Capacity (16개) - 용량/출력 사양
* Dimension (16개) - 물리적 치수
* Temperature (4개) - 온도 조건
* 모든 기술적 요구사항을 측정 가능한 값으로 구조화

🏗️ 핵심 클래스 계층

* Performance (38개) - 성능 요구사항
* Requirement (19개) - 일반 요구사항
* Chapter (17개) - FSS 코드 챕터
* Capacity/Dimension (16개씩) - 용량/치수 사양
* ExtinguishingSystem (11개) - 소화 시스템
* Component (9개) - 시스템 구성요소

📚 Chapter 클래스 → 17개 인스턴스

각 챕터는 여러 시스템을 다룹니다:

* Chapter1 → ApplicationRule, ToxicMediumRule
* Chapter3 → FireFightersOutfit, EEBD
* Chapter5 → CO2System, NitrogenSystem
* Chapter6 → HighExpansionFoamSystem, LowExpansionFoamSystem, etc.



🔥 ExtinguishingSystem 클래스 → 11개 인스턴스

구체적인 소화 시스템들:

* CO2System, NitrogenSystem
* HighExpansionFoamSystem, LowExpansionFoamSystem
* WaterSprayingSystem, WaterMistSystem
* DeckFoamSystem, HelideckFoamSystem



⚙️ Component 클래스 → 9개 인스턴스

시스템 구성요소들:

* SprinklerHead, SprinklerControlUnit
* SensingUnit, SamplingPipe
* InertGasGenerator, GasDistributionSystem
* 

📋 Specification 클래스 → 구체적인 사양들

* Shore_Connection_Spec_Pressure = "1.0 N/mm²"
* DeckHeightSpec, CableRequirement, etc.



📊 프로퍼티 분류

1. 구조적 관계 프로퍼티 (Object Properties)

* hasSpecification (84회) - 시스템/컴포넌트 → 사양
* detailsSystem (31회) - 챕터 → 시스템
* appliesTo (20회) - 시스템 → 적용 대상
* hasComponent (6회) - 시스템 → 구성요소
* partOf - 구성요소 → 상위 시스템

2. 데이터 프로퍼티 (Data Properties)

* value (38회) - 구체적인 값 (예: "1,200 l", "5 kg")
* requiredTime (19회) - 시간 요구사항 (예: "30 min")
* hasDuration (8회) - 지속 시간
* hasDimension (7회) - 치수 정보
* hasTemperature (5회) - 온도 값

3. 메타데이터 프로퍼티

* rdf:type (186회) - 클래스 분류(각 인스턴스가 어떤 클래스에 속하는지를 정의)
* rdfs:label (29회) - 라벨/이름
* rdfs:comment (114회) - 설명/주석



시스템 구조 패턴:

* Chapter --detailsSystem→ ExtinguishingSystem
* ExtinguishingSystem --hasSpecification→ Performance
* ExtinguishingSystem --hasComponent→ Component
* ExtinguishingSystem --appliesTo→ ProtectedSpace

사양 정의 패턴:

* Performance --value→ "구체적 값"
* Performance --requiredTime→ "시간"
* Capacity --value→ "용량"
* Dimension --value→ "치수"

