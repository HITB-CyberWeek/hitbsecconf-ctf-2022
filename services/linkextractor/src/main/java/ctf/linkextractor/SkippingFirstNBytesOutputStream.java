package ctf.linkextractor;

import java.io.IOException;
import java.io.OutputStream;

public class SkippingFirstNBytesOutputStream extends OutputStream {

    int skipped = 0;
    private OutputStream stream;
    int bytesToSkip;

    public SkippingFirstNBytesOutputStream(OutputStream stream, int bytesToSkip) {
        this.stream = stream;
        this.bytesToSkip = bytesToSkip;
    }

    @Override
    public void write(int b) throws IOException {
        if (skipped < bytesToSkip)
            skipped++;
        else
            stream.write(b);
    }
}
