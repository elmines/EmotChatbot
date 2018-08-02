"""
Utility module for generating word embeddings
"""
import gensim
import numpy as np
import pandas as pd

import sys

#Local modules
import match

def w2vec(model_path, text, vocab2int, embedding_size=1024, verbose=True):
	"""
	Generates Word2Vec embeddings

	:param path-like       model_path: The path at which to save the embeddings before returning
	:param list(list(str))       text: The tokens from which to generate the embeddings, where text[i][j] is the jth token of the ith sequence
	:param dict(str,int)    vocab2int: A mapping from tokens in the vocabulary to their integer indices
	:param bool               verbose: Print helpful messages to stderr
	
	:returns: The generated embeddings
	:rtype:   np.ndarray
	"""
	if verbose: sys.stderr.write("Learning Word2Vec embeddings on {} sequences . . .\n".format(len(text)))
	model = gensim.models.Word2Vec(sentences=text, size=embedding_size, window=5, min_count=1, workers=4, sg=0)
	word_vecs = np.zeros((len(model.wv.vocab),embedding_size))
	for i,word in enumerate(model.wv.index2word):
        	word_vecs[vocab2int[word]] = model[word]

	np.save(model_path,word_vecs)
	if verbose: sys.stderr.write("Wrote Word2Vec model to {}\n".format(model_path))

	return word_vecs


def appended_vad(model_path, embeddings, vocab2int, exclude=None, verbose=True):
	"""
	Appends VAD (Valence, Arousal, Dominance) values to existing word embeddings

	:param path-like       model_path: The path at which to save the new embeddings before returning
	:param np.ndarray      embeddings: The original embeddings
	:param dict(str,int)    vocab2int: A mapping from tokens in the vocabulary to their integer indices
	:param list(str)          exclude: A list of tokens in vocab2int for which to assign the neutral vector (such as the unknown token)
	:param bool               verbose: Print helpful messages to stderr
	
	:returns: The generated embeddings
	:rtype:   np.ndarray
	"""
	#Simple list of vocabulary items at their proper indices
	int2vocab = sorted(vocab2int.keys(), key=vocab2int.__getitem__)

	df_vad=pd.read_excel('Warriner, Kuperman, Brysbaert - 2013 BRM-ANEW expanded.xlsx')
	df_vad["Word"] = df_vad["Word"].apply(str)
	targ_vocab = list(df_vad["Word"])

	mapping = match.vocab_match(int2vocab, targ_vocab, verbose=verbose)
	if exclude is not None:
		for word in exclude:
			mapping[word] = None

	embedding_size = embeddings.shape[1]
	word_vecs_vad = np.zeros( (len(vocab2int), embedding_size+3) )
	count_vad=0
	count_neutral=0
	for word in int2vocab:
		target_word = mapping[word]
		index = vocab2int[word]
		if target_word is not None:
			if verbose: sys.stderr.write("VAD Values Assigned: {} --> {}\n".format(word, target_word))
			count_vad += 1
			word_vecs_vad[index][:-3] = embeddings[index]
			word_vecs_vad[index][-3] = df_vad.loc[df_vad['Word'] == target_word, 'V.Mean.Sum'].iloc[0]
			word_vecs_vad[index][-2] = df_vad.loc[df_vad['Word'] == target_word, 'A.Mean.Sum'].iloc[0]
			word_vecs_vad[index][-1] = df_vad.loc[df_vad['Word'] == target_word, 'D.Mean.Sum'].iloc[0]
		else:
			if verbose: sys.stderr.write("Neutral Vector Assigned: {}\n".format(word))
			count_neutral += 1
			word_vecs_vad[index][:-3] = embeddings[index]
			word_vecs_vad[index][-3]   = 5
			word_vecs_vad[index][-2]   = 1
			word_vecs_vad[index][-1]   = 5

	np.save(model_path,word_vecs_vad)

	if verbose:
		sys.stderr.write("{}/{} words assigned corresponsing VAD values.\n".format(count_vad, len(vocab2int)))
		sys.stderr.write("{}/{} words assigned the neutral VAD vector.\n".format(count_neutral, len(vocab2int)))
	
	return word_vecs_vad


def aff2vec(model_path, vocab2int, aff_embeddings_path="./w2_counterfit_append_affect.bin", exclude=None, verbose=True):
	"""
	Extracts Aff2Vec embeddings for an arbitary vocabulary from an existing word embeddings .bin file

	For words in the vocabulary but not the .bin file, the function creates a \"neutral embedding\" which is simply the average of all the embedding
	vectors assigned for words that were found.

	:param path-like               model_path: The path at which to save the new embeddings before returning
	:param dict(str,int)            vocab2int: A mapping from tokens in the vocabulary to their integer indices
	:param path-like      aff_embeddings_path: Path to a .bin gensim file
	:param list(str)                  exclude: A list of tokens in vocab2int for which to assign the neutral vector (such as the unknown token)
	:param bool                       verbose: Print helpful messages to stderr
	
	:returns: The extracted embeddings
	:rtype:   np.ndarray
	"""

	#Simple list of vocabulary items at their proper indices
	#FIXME: Assumes the lowest index is indeed 0. Bad?
	int2vocab = sorted(vocab2int.keys(), key=vocab2int.__getitem__)

	# Load Google's pre-trained Word2Vec model.
	aff_embeddings = gensim.models.KeyedVectors.load_word2vec_format(aff_embeddings_path, binary=True)

	targ_vocab = list(aff_embeddings.wv.vocab.keys())
	mapping = match.vocab_match(int2vocab, targ_vocab, verbose=verbose)
	if exclude is not None:
		for word in exclude:
			mapping[word] = None

	embedding_size = len(aff_embeddings.wv[targ_vocab[0]])
	word_vecs_emot = np.zeros( (len(vocab2int), embedding_size) )

	assign_emot = []
	assign_neutral = []

	for word in int2vocab:
		target_word = mapping[word]
		word_index = vocab2int[word]
		if target_word is not None:
			if verbose: sys.stderr.write("Emotional Embeddings Assigned: {} --> {}\n".format(word, target_word))
			assign_emot.append(word_index)
			word_vecs_emot[word_index] = aff_embeddings.wv[target_word]

		else:
			if verbose: sys.stderr.write("Neutral Vector Assigned: {}\n".format(word))
			assign_neutral.append(word_index)


	neut_embedding = np.mean( word_vecs_emot[assign_emot], axis = 0)
	word_vecs_emot[assign_neutral] = neut_embedding
	np.save(model_path, word_vecs_emot)

	if verbose:
		sys.stderr.write("{}/{} words assigned emotional embeddings.\n".format(len(assign_emot), len(vocab2int)))
		sys.stderr.write("{}/{} words assigned the neutral vector.\n".format(len(assign_neutral), len(vocab2int)))

	return word_vecs_emot
