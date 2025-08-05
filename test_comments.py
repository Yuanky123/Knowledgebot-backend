# 一些能够被fine-tuned LLM 正确识别的comment测试用例
post = "How can we make people living in city happy?"

test_comments = [
    # Initiation, argument 1
    "I think it is important to have good public transportations so that people won't spend a lot of time commuting.",
    # Exploration: evidence, reasoning, qualifier
    "Yes, Studies show that cities with efficient public transportation systems, like Tokyo and Zurich, have significantly shorter average commute times compared to car-dependent cities.",
    "I agree. It shows that good public transportation can reduce commute times, directly addressing the concern about long commuting.",
    "This claim is likely to be correct in densely populated urban areas where many people rely on daily commuting for work or school.",
    # counterargument
    "I disagree because even with good public transportation, delays and overcrowding can still make commuting stressful and time-consuming.",
    # evidence, reasoning, qualifier
    "Exactly. For example, in cities like New York, public transit is often delayed or overcrowded during peak hours.",
    "Yes. This shows that even well-developed systems can struggle to provide a smooth commuting experience.",
    "This is especially true in cities where infrastructure is aging or underfunded.",

    # Negotiation: phase 3
    "You're right that even the best public transport systems aren't perfect—delays and overcrowding do cause stress. But I think both sides actually agree on the core issue: commuting time and quality affect urban happiness. Maybe the focus shouldn't just be on having public transport, but on improving its reliability, comfort, and accessibility.",

    # Initiation, argument 2
    "I think we should enforce strict labor laws so that people don't overwork.",
    # Exploration: evidence, reasoning, qualifier
    "Yes, for example, countries like France and Germany have strong labor protections and report higher work-life satisfaction among urban workers.",
    "Exactly, when people work fewer hours, they have more time to rest, socialize, and enjoy life, which contributes to overall happiness.",
    "I agree, especially in high-pressure industries or cities where long work hours are normalized and burnout is common.",
    
    # Initiation, argument 3
    "We should make connections among neighborhood to build a strong community",
    # Exploration: evidence, reasoning, qualifier
    "Yes, studies have shown that people who know their neighbors tend to feel safer and report higher levels of life satisfaction.",
    "Agreed. Stronger social ties can reduce loneliness",
    "I agree, especially in urban areas where people often feel isolated despite living close to others.",
]