import { Routes } from '@angular/router';

export const ImageConversionRoutes: Routes = [
    {
        path: '',
        loadComponent: () => import('./image-conversion.component').then(c => c.ImageConversionComponent)
    },
    {
        path: 'png-to-json-ai',
        loadComponent: () => import('./png-to-json-ai/png-to-json-ai.component').then(c => c.PngToJsonAiComponent)
    },
    {
        path: 'jpg-to-json-ai',
        loadComponent: () => import('./jpg-to-json-ai/jpg-to-json-ai.component').then(c => c.JpgToJsonAiComponent)
    },
    {
        path: 'jpg-to-pdf',
        loadComponent: () => import('./jpg-to-pdf/jpg-to-pdf.component').then(c => c.JpgToPdfComponent)
    },
    {
        path: 'png-to-pdf',
        loadComponent: () => import('./png-to-pdf/png-to-pdf.component').then(c => c.PngToPdfComponent)
    },
    {
        path: 'website-to-jpg',
        loadComponent: () => import('./website-to-jpg/website-to-jpg.component').then(c => c.WebsiteToJpgComponent)
    },
    {
        path: 'html-to-jpg',
        loadComponent: () => import('./html-to-jpg/html-to-jpg.component').then(c => c.HtmlToJpgComponent)
    },
    {
        path: 'website-to-png',
        loadComponent: () => import('./website-to-png/website-to-png.component').then(c => c.WebsiteToPngComponent)
    },
    {
        path: 'html-to-png',
        loadComponent: () => import('./html-to-png/html-to-png.component').then(c => c.HtmlToPngComponent)
    },
    {
        path: 'pdf-to-jpg',
        loadComponent: () => import('./pdf-to-jpg/pdf-to-jpg.component').then(c => c.PdfToJpgComponent)
    },
    {
        path: 'pdf-to-png',
        loadComponent: () => import('./pdf-to-png/pdf-to-png.component').then(c => c.PdfToPngComponent)
    },
    {
        path: 'pdf-to-tiff',
        loadComponent: () => import('./pdf-to-tiff/pdf-to-tiff.component').then(c => c.PdfToTiffComponent)
    },
    {
        path: 'pdf-to-svg',
        loadComponent: () => import('./pdf-to-svg/pdf-to-svg.component').then(c => c.PdfToSvgComponent)
    },
    {
        path: 'ai-to-svg',
        loadComponent: () => import('./ai-to-svg/ai-to-svg.component').then(c => c.AiToSvgComponent)
    },
    {
        path: 'png-to-svg',
        loadComponent: () => import('./png-to-svg/png-to-svg.component').then(c => c.PngToSvgComponent)
    },
    {
        path: 'png-to-avif',
        loadComponent: () => import('./png-to-avif/png-to-avif.component').then(c => c.PngToAvifComponent)
    },
    {
        path: 'jpg-to-avif',
        loadComponent: () => import('./jpg-to-avif/jpg-to-avif.component').then(c => c.JpgToAvifComponent)
    },
    {
        path: 'webp-to-avif',
        loadComponent: () => import('./webp-to-avif/webp-to-avif.component').then(c => c.WebpToAvifComponent)
    },
    {
        path: 'avif-to-png',
        loadComponent: () => import('./avif-to-png/avif-to-png.component').then(c => c.AvifToPngComponent)
    },
    {
        path: 'avif-to-jpeg',
        loadComponent: () => import('./avif-to-jpeg/avif-to-jpeg.component').then(c => c.AvifToJpegComponent)
    },
    {
        path: 'avif-to-webp',
        loadComponent: () => import('./avif-to-webp/avif-to-webp.component').then(c => c.AvifToWebpComponent)
    },
    {
        path: 'png-to-webp',
        loadComponent: () => import('./png-to-webp/png-to-webp.component').then(c => c.PngToWebpComponent)
    },
    {
        path: 'jpg-to-webp',
        loadComponent: () => import('./jpg-to-webp/jpg-to-webp.component').then(c => c.JpgToWebpComponent)
    },
    {
        path: 'tiff-to-webp',
        loadComponent: () => import('./tiff-to-webp/tiff-to-webp.component').then(c => c.TiffToWebpComponent)
    },
    {
        path: 'gif-to-webp',
        loadComponent: () => import('./gif-to-webp/gif-to-webp.component').then(c => c.GifToWebpComponent)
    },
    {
        path: 'webp-to-png',
        loadComponent: () => import('./webp-to-png/webp-to-png.component').then(c => c.WebpToPngComponent)
    },
    {
        path: 'webp-to-jpeg',
        loadComponent: () => import('./webp-to-jpeg/webp-to-jpeg.component').then(c => c.WebpToJpegComponent)
    },
    {
        path: 'webp-to-tiff',
        loadComponent: () => import('./webp-to-tiff/webp-to-tiff.component').then(c => c.WebpToTiffComponent)
    },
    {
        path: 'webp-to-bmp',
        loadComponent: () => import('./webp-to-bmp/webp-to-bmp.component').then(c => c.WebpToBmpComponent)
    },
    {
        path: 'webp-to-yuv',
        loadComponent: () => import('./webp-to-yuv/webp-to-yuv.component').then(c => c.WebpToYuvComponent)
    },
    {
        path: 'webp-to-pam',
        loadComponent: () => import('./webp-to-pam/webp-to-pam.component').then(c => c.WebpToPamComponent)
    },
    {
        path: 'webp-to-pgm',
        loadComponent: () => import('./webp-to-pgm/webp-to-pgm.component').then(c => c.WebpToPgmComponent)
    },
    {
        path: 'webp-to-ppm',
        loadComponent: () => import('./webp-to-ppm/webp-to-ppm.component').then(c => c.WebpToPpmComponent)
    },
    {
        path: 'png-to-jpg',
        loadComponent: () => import('./png-to-jpg/png-to-jpg.component').then(c => c.PngToJpgComponent)
    },
    {
        path: 'png-to-pgm',
        loadComponent: () => import('./png-to-pgm/png-to-pgm.component').then(c => c.PngToPgmComponent)
    },
    {
        path: 'png-to-ppm',
        loadComponent: () => import('./png-to-ppm/png-to-ppm.component').then(c => c.PngToPpmComponent)
    },
    {
        path: 'jpg-to-png',
        loadComponent: () => import('./jpg-to-png/jpg-to-png.component').then(c => c.JpgToPngComponent)
    },
    {
        path: 'jpeg-to-pgm',
        loadComponent: () => import('./jpeg-to-pgm/jpeg-to-pgm.component').then(c => c.JpegToPgmComponent)
    },
    {
        path: 'jpeg-to-ppm',
        loadComponent: () => import('./jpeg-to-ppm/jpeg-to-ppm.component').then(c => c.JpegToPpmComponent)
    },
    {
        path: 'heic-to-png',
        loadComponent: () => import('./heic-to-png/heic-to-png.component').then(c => c.HeicToPngComponent)
    },
    {
        path: 'heic-to-jpg',
        loadComponent: () => import('./heic-to-jpg/heic-to-jpg.component').then(c => c.HeicToJpgComponent)
    },
    {
        path: 'svg-to-png',
        loadComponent: () => import('./svg-to-png/svg-to-png.component').then(c => c.SvgToPngComponent)
    },
    {
        path: 'svg-to-jpg',
        loadComponent: () => import('./svg-to-jpg/svg-to-jpg.component').then(c => c.SvgToJpgComponent)
    },
    {
        path: 'remove-exif',
        loadComponent: () => import('./remove-exif/remove-exif.component').then(c => c.RemoveExifComponent)
    }
];
