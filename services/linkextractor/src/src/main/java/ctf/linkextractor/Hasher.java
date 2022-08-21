package ctf.linkextractor;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.Formatter;

public class Hasher {
    private static final String HMAC_SHA512 = "HmacSHA512";
    private static byte[] macKey;
    Mac mac;
    public static final Hasher singletone = new Hasher();

    private Hasher(){
        Path keyPath = Paths.get("secret/macKey");
        try {
            macKey = Files.readAllBytes(keyPath);
        } catch (IOException e) {
            macKey = new byte[128];
            SecureRandom secureRandom = new SecureRandom();
            secureRandom.nextBytes(macKey);
            try {
                Files.createDirectories(keyPath.getParent());
                Files.write(keyPath, macKey, StandardOpenOption.CREATE);
            } catch (IOException ex) {
                throw new RuntimeException(ex);
            }
        }

        try {
            mac = Mac.getInstance(HMAC_SHA512);
            SecretKeySpec secretKeySpec = new SecretKeySpec(macKey, HMAC_SHA512);
            mac.init(secretKeySpec);
        } catch (NoSuchAlgorithmException | InvalidKeyException e) {
            throw new RuntimeException(e);
        }
    }

    private String toHexString(byte[] bytes) {
        Formatter formatter = new Formatter();
        for (byte b : bytes)
            formatter.format("%02x", b);
        return formatter.toString();
    }

    public String calculateHMAC(String data)
    {
        return toHexString(mac.doFinal(data.getBytes()));
    }
}
