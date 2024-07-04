import nltk
from nltk.corpus import wordnet
import random
    


    
"""
# Baixar os recursos necessários do NLTK
nltk.download('omw')
nltk.download('omw-1.4')
nltk.download('wordnet')



# Função para supressão de palavras
def word_dropout(sentence, dropout_prob=0.2):
    words = sentence.split()
    new_words = [word for word in words if random.random() > dropout_prob]
    return ' '.join(new_words)

# Função para aplicar data augmentation
def augment_sentence(sentence):
    augmented_sentences = set()
    
    # Supressão de palavras
    augmented_sentences.add(word_dropout(sentence))
    
    return list(augmented_sentences)

# Exemplo de frases
sentences = [

]

# Aplicando data augmentation
augmented_sentences = []
for sentence in sentences:
    augmented_sentences.extend(augment_sentence(sentence))

# Número de exemplos originais e aumentados
print("Exemplos originais:", len(sentences))
print("Exemplos aumentados:", len(augmented_sentences))

# Imprimir os exemplos aumentados
for augmented_sentence in augmented_sentences:
    print(augmented_sentence)


"""

"""
from augly.text import functional as augf
import nlpaug.augmenter.char as nac
from textattack.augmentation import CharSwapAugmenter


text = "Example sentence for augmentation."
augmented_text = augf.simulate_typos(text)
print(augmented_text)


# Create an augmenter that simulates keyboard typos
aug = nac.KeyboardAug()
text = "This is a test sentence."
augmented_text = aug.augment(text)
print(augmented_text)


# Create an augmenter with a specific probability of character swap
augmenter = CharSwapAugmenter(pct_words_to_swap=0.1, transformations_per_example=1)
sentences = ["This is an example sentence."]
augmented_sentences = augmenter.augment(sentences[0])
print(augmented_sentences)
"""
