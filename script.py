import os
import re
import streamlit as st 

@st.cache_resource
def load_word_freq_dict(dict_path='ru_en_dict.tsv'):
    print(f"Загрузка словаря частот из файла '{dict_path}'")

    if not os.path.exists(dict_path):
        st.error(f"Критическая ошибка: Файл словаря '{dict_path}' не найден!")
        return None
    
    freq_dict = {}
    one_letter_whitelist = {'в', 'с', 'и', 'к', 'у', 'а', 'a', 'i'}

    with open(dict_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                word, freq = parts
                if len(word) > 1 or word in one_letter_whitelist:
                    freq_dict[word] = float(freq)
    
    for word in one_letter_whitelist:
        if word not in freq_dict: 
            freq_dict[word] = 5.0
        
    print(f"Словарь готов. Уникальных слов: {len(freq_dict)}")
    return freq_dict


def segment_text(text, freq_dict):
    n = len(text)
    memo = {0: (0.0, 0)}
    unknown_word_freq = -20.0

    for i in range(1, n + 1):
        best_score = -float('inf')
        best_len = 0
        max_word_len = min(i, 25) 

        for k in range(1, max_word_len + 1):
            start_pos = i - k
            word = text[start_pos:i]
            
            word_len_bonus = len(word) ** 2
            base_freq = freq_dict.get(word, unknown_word_freq)
            current_word_score = base_freq * word_len_bonus
            
            prev_score, _ = memo.get(start_pos, (-float('inf'), 0))
            current_total_score = prev_score + current_word_score

            if current_total_score > best_score:
                best_score = current_total_score
                best_len = k

        memo[i] = (best_score, best_len)

    words = []
    i = n
    while i > 0:
        _, k = memo[i]
        if k == 0: break
        words.append(text[i-k:i])
        i -= k

    return words[::-1]


def segmenter(text, freq_dict):
    pattern = r'([а-яё]+|[a-z]+|[0-9]+|[^а-яёa-z0-9\s]+)'
    parts = re.findall(pattern, text.lower())
    
    raw_tokens = []
    for part in parts:
        if not part: continue
        
        if re.fullmatch(r'[а-яё]+', part) or re.fullmatch(r'[a-z]+', part):
            raw_tokens.extend(segment_text(part, freq_dict))
        else:
            raw_tokens.append(part)

    if not raw_tokens:
        return ""

    final_tokens = [raw_tokens[0]]
    punctuation_pattern = r'^[.,!?;:)\]}]+$'
    for token in raw_tokens[1:]:
        if re.fullmatch(punctuation_pattern, token) and final_tokens:
            final_tokens[-1] += token
        else:
            final_tokens.append(token)
            
    return " ".join(final_tokens)


def restore_spaces(text):
    word_freq_dict = load_word_freq_dict()
    if word_freq_dict is None:
        return "Ошибка: не удалось загрузить словарь частот."

    restored_text = segmenter(text, word_freq_dict)
    
    return restored_text