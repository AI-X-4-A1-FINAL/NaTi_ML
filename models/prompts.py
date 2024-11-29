# prompts.py

# 게임 세계관 생성용 프롬프트 사전 정의
def game_prompt(genre: str, world_description: str) -> str:
    """
    게임 장르와 세계관 설명을 기반으로 프롬프트를 생성
    :param genre: 게임 장르 (예: 판타지, 공상과학 등)
    :param world_description: 세계관에 대한 설명
    :return: 생성된 프롬프트 문자열
    """
    return (
        f"지금 '{genre}' 장르에 맞는 게임 세계관을 만들어줘. "
        f"세계관 설명: {world_description}. "
        "이 세계는 판타지적 요소가 포함되어야 하며, "
        "주요 도시와 NPC, 몬스터 유형까지 포함하여 상세히 설명해줘. "
        "한 번에 200자 이내로 말하고, 계속 이어서 스토리를 만들어줘."
    )
