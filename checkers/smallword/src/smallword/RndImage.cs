using System;
using System.IO;
using checker.rnd;
using SkiaSharp;

namespace checker.smallword;

public static class RndImage
{
    public static void Generate(int width, int height, Stream stream, out string format)
    {
        using var surface = SKSurface.Create(new SKImageInfo(width, height, SKColorType.Argb4444));
        using var canvas = surface.Canvas;
        canvas.Clear(SKColors.Black);

        GenCircles(canvas, width, height);

        using var image = surface.Snapshot();
        var imgFormat = RndUtil.Choice(SKEncodedImageFormat.Png, SKEncodedImageFormat.Jpeg);
        format = imgFormat.ToString().ToLowerInvariant();
        using var data = image.Encode(imgFormat, 80);

        data.SaveTo(stream);

        GC.KeepAlive(canvas);
        GC.KeepAlive(surface);
    }

    private static void GenCircles(SKCanvas canvas, int width, int height)
    {
        var paint = new SKPaint {IsAntialias = true};
        var min = Math.Min(width, height);
        for(int i = 0; i < RndUtil.GetInt(20, 30); i++)
        {
            var diameter = RndUtil.GetInt(min / 8, min / 2);
            var radius = diameter / 2;

            var cx = RndUtil.GetInt(-radius, width + radius);
            var cy = RndUtil.GetInt(-radius, height + radius);

            paint.Style = SKPaintStyle.Fill;
            paint.Color = SKColor.FromHsl(RndUtil.GetInt(0, 256), RndUtil.GetInt(128, 256), RndUtil.GetInt(128, 256), (byte)RndUtil.GetInt(64, 192));
            canvas.DrawRect(cx, cy, diameter, diameter, paint);

            paint.Style = SKPaintStyle.Stroke;
            paint.Color = SKColor.FromHsl(RndUtil.GetInt(0, 256), RndUtil.GetInt(192, 256), RndUtil.GetInt(192, 256), (byte)RndUtil.GetInt(128, 192));
            canvas.DrawRect(cx, cy, diameter, diameter, paint);
        }
    }
}