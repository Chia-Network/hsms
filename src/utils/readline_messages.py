
async def reader_to_readline_stream(reader):
    """
    This adaptor accepts a reader and turns it into a generator that yields
    messages (in the form of lines) read from the reader.
    """
    while True:
        line = await reader.readline()
        # if the connection is closed, we get a line of no bytes
        if len(line) == 0:
            break
        yield line
