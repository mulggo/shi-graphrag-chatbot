#!/usr/bin/env python3
"""
참조 표시 모듈 테스트
"""

import streamlit as st
from ui.reference_display import ReferenceDisplay

# 더미 참조 데이터 (Plan-Execute Agent 형식)
dummy_references = [
    {
        'id': 'ref_1',
        'content': 'SOLAS Chapter II-2 requires ships to have fire extinguishers, fire detection systems, and sprinkler systems for fire safety.',
        'source': 'SOLAS_Chapter_II-2.pdf',
        'score': 0.8
    },
    {
        'id': 'ref_2', 
        'content': 'FSS Code specifies the requirements for fire safety systems including portable fire extinguishers and fixed fire fighting systems.',
        'source': 'FSS_Code.pdf',
        'score': 0.7
    }
]

st.title("참조 표시 모듈 테스트")

# ReferenceDisplay 테스트
display = ReferenceDisplay()

st.markdown("## 테스트 참조 데이터")
st.json(dummy_references)

st.markdown("## 렌더링 결과")
display.render_references(dummy_references)