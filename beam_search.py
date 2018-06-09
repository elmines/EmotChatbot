import tensorflow as tf
import collections


class CustomBeamSearchDecoderOutput(
	collections.namedtuple("BeamSearchDecoderOutput",
                           ("scores", "predicted_ids", "parent_ids"))):
	pass

class CustomBeamSearchDecoderState(
	collections.namedtuple("BeamSearchDecoderState",
                           ("cell_state", "log_probs", "augmented_probs", "finished", "lengths"))):

	"""
	augumented_probs - The log probabilities of the generated sequences, plus the additional custom term added by the user
	"""
	pass




class CustomBeamSearchDecoder: #(tf.Decoder)
	"""
	Allows the addition of an additional term to the beam search optimization equation
        """

	def __init__(cell,
       			embedding,
                        start_token,
                        end_token,
                        initial_state,
			batch_size,
                        beam_width,
                        output_fn = None,
			strength = 0.0 #Weight to be applied to the additional term
                        search_style=None):

		"""
		cell - An instance of RNN cell
		embedding - An embedding matrix for decoded words
		start_token - Initial token to feed into decoder for each sample
        	end_token - Token that causes the decoder to stop for a beam
		initial_state - Initial state of the decoder cell
		batch_size - The number of samples in the batch
		beam_width - Number of beams to maintain in decoding
        	output_fn - A function (need not be a layer) to apply to RNN outputs
        	search_style - FUTURE WORK: style of beam search to use (diverse, affectively diverse, etc.)
        	"""
		self._cell = cell
		self._embedding = embedding

		self._start_token = start_token
		self._end_token = end_token

		self._initial_cell_state = initial_state

		self._beam_width = beam_width
		self._output_fn = output_fn
		self._search_style = search_style

		self._batch_size = batch_size #FIXME: Have the user pass this in as a parameter, or compute it from another input?

                self._finished_beams = tf.zeros([self.batch_size, self.beam_width], dtype=tf.bool)

		#The "zeros" are, expectedly, converted to `False` values
		self._finished = tf.zeros(self.batch_size, dtype=tf.bool)

		
	@property
	def batch_size(self):
		return self._batch_size

	@property
	def tracks_own_finished_state():
		"""
		Like tf.contrib.seq2seq.BeamSearchDecoder, our decoder's shuffling of beams will confuse tf.contrib.seq2seq.dynamic_decode
		Returns `True`
		"""
		return True
	

	def finalize(self, outputs, final_state, sequence_lengths, name=None):
		pass

	def initialize(self, name=None):
		"""
		Returns
			finished - A tf.bool array of size [batch_size] denoting which samples are finished (obviously all `False` initially)
			initial_inputs - The initial inputs to be fed into the decoder cell
			initial_state - The state with which to initialize the decoder cell	
		"""
		with tf.name_scope(name):
			#FIXME: Find another way to pass along the name without wasting memory using tf.identity? 
			finished = tf.identity(self._finished)

			initial_state = 

			initial_inputs = None
			initial_state = None

		return (finished, initial_inputs, initial_state)

	def step(self, time, inputs, state):

		outputs = None
		next_state = None
		next_input = None
		finished = None

		return (outputs, next_state, next_input, finished)

		pass

