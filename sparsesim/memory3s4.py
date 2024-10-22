    def compress_to_ellpack_block(self, matrix, filter_op_mat):
        # Each entry of the original matrix requires 1 word size
        # Each entry in filter_op_mat will require 2 bits of metadata
        original_rows, original_cols = matrix.shape
        new_rows, new_cols = filter_op_mat.shape

        original_storage = original_rows * original_cols # Units: Words
        metadata_storage = ((new_rows * new_cols) * 2) / 32 # Units: Words (considering 1 word = 4 bytes = 32 bits)
        new_storage = (new_rows * new_cols) + metadata_storage # Units: Words (considering 1 word = 4 bytes = 32 bits)

        return original_storage, new_storage, metadata_storage