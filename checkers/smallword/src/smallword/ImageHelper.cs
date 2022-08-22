using System;
using System.IO;
using SkiaSharp;

namespace checker.smallword;

public static class ImageHelper
{
    public static bool Equals(Stream img1, Stream img2)
    {
        using var bmp1 = SKBitmap.Decode(img1);
        using var bmp2 = SKBitmap.Decode(img2);

        var pixels1 = bmp1.Pixels;
        var pixels2 = bmp2.Pixels;

        for(var i = 0; i < bmp1.Width * bmp1.Height; i++)
        {
            if(pixels1[i] != pixels2[i])
                return false;
        }

        GC.KeepAlive(bmp1);
        GC.KeepAlive(bmp2);

        return true;
    }
}