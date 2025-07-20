#!/usr/bin/env python3
"""
MOHU 哲学示例演示

展示同音字背后的人生哲理：
"长大后才发现，北京就是背景，上海就是商海，彩礼就是财力，而理想就是离乡"
"""

from mohu import MohuMatcher

def main():
    print("🎭 MOHU 哲学匹配演示")
    print("=" * 50)
    print()
    print("💭 哲学名言：")
    print("   \"长大后才发现，北京就是背景，上海就是商海，")
    print("    彩礼就是财力，而理想就是离乡\"")
    print()
    
    # 构建人生词典
    life_words = [
        # 经典哲学对应
        "北京", "背景", "上海", "商海",
        "彩礼", "财力", "理想", "离乡",
        # 扩展的人生感悟
        "奋斗", "愤怒", "成功", "成空", 
        "青春", "轻纯", "岁月", "碎月",
        "知识", "之时", "经验", "惊艳",
        "坚持", "坚实", "梦想", "蒙想"
    ]

    matcher = MohuMatcher()
    matcher.build(life_words)

    print("🌟 人生哲学匹配验证：")
    print("=" * 50)

    # 核心哲学对应关系
    philosophical_pairs = [
        ("北京", "在这座城市里，每个人都只是..."),
        ("上海", "在商业的海洋中，我们都在..."), 
        ("彩礼", "表面的仪式，实质考验的是..."),
        ("理想", "追求梦想的代价往往是...")
    ]

    # 验证核心哲学对应
    for word, description in philosophical_pairs:
        print(f"\n🔍 搜索: '{word}'")
        print(f"   💭 {description}")
        
        # 使用拼音模式发现同音字
        results = matcher.match(word, mode='pinyin', max_results=5)
        
        found_philosophy = False
        for match_word, score in results:
            if match_word != word and score > 0.8:  # 找到高度相似的同音字
                print(f"   💫 发现同音奥秘: {word} ≈ {match_word} (相似度: {score:.2f})")
                found_philosophy = True
        
        if not found_philosophy:
            print(f"   🔍 拼音匹配结果: {[(w, f'{s:.2f}') for w, s in results[:3]]}")
        
        # 展示混合模式的智能匹配
        hybrid_results = matcher.match(word, mode='hybrid', max_results=3)
        print(f"   🎯 混合模式: {[f'{w}({s:.2f})' for w, s in hybrid_results]}")

    print("\n" + "=" * 50)
    
    # 展示更多人生感悟的同音字发现
    print("\n🌟 探索更多人生同音智慧：")
    print("=" * 50)
    
    life_concepts = ["奋斗", "青春", "成功", "知识", "坚持", "梦想"]
    
    for concept in life_concepts:
        results = matcher.match(concept, mode='pinyin', max_results=8)
        
        print(f"\n🎨 '{concept}' 的同音变奏：")
        similar_words = []
        for word, score in results:
            if word != concept and score >= 0.8:
                similar_words.append(f"{word}({score:.2f})")
        
        if similar_words:
            print(f"   {' → '.join(similar_words)}")
        else:
            print(f"   暂未发现高度相似的同音词汇")

    print("\n" + "=" * 50)
    print("✨ 语言的魅力：")
    print("   同音不同义，MOHU 帮你发现文字背后的哲学深意！")
    print("   技术与人文的完美结合，让每一次搜索都充满诗意。")
    print("=" * 50)

    # 交互式探索
    print("\n🎯 试试你的同音字哲学发现：")
    while True:
        user_input = input("\n请输入一个词汇探索其同音奥秘 (输入'quit'退出): ").strip()
        
        if user_input.lower() in ['quit', 'exit', '退出', 'q']:
            print("👋 感谢使用 MOHU 哲学探索！愿你在文字的海洋中发现更多智慧。")
            break
        
        if not user_input:
            continue
            
        print(f"\n🔍 探索 '{user_input}' 的同音世界：")
        
        # 动态添加用户词汇
        if user_input not in matcher.get_words():
            matcher.add_word(user_input)
            print(f"   ➕ 已将 '{user_input}' 添加到词典")
        
        # 拼音匹配
        pinyin_results = matcher.match(user_input, mode='pinyin', max_results=5)
        print(f"   🎵 拼音相似: {[f'{w}({s:.2f})' for w, s in pinyin_results[:3]]}")
        
        # 字符匹配
        char_results = matcher.match(user_input, mode='char', max_results=5)
        print(f"   ✍️  字形相似: {[f'{w}({s:.2f})' for w, s in char_results[:3]]}")
        
        # 混合匹配
        hybrid_results = matcher.match(user_input, mode='hybrid', max_results=3)
        print(f"   🌟 智能匹配: {[f'{w}({s:.2f})' for w, s in hybrid_results]}")

if __name__ == "__main__":
    main() 