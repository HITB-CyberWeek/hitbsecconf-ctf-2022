package ctf.linkextractor;

import java.io.ObjectInputFilter;

public class EntitiesObjectInputFilter implements ObjectInputFilter {
    public Status checkInput(FilterInfo filterInfo) {
        Class<?> clazz = filterInfo.serialClass();
        if (clazz != null && filterInfo.depth() == 1) {
            String clazzName = clazz.getName();
            return clazzName.startsWith("ctf.linkextractor.entities.") ? Status.ALLOWED : Status.REJECTED;
        }
        return Status.UNDECIDED;
    }
}
