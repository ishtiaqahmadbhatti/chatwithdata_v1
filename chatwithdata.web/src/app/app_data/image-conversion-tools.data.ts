import { ConversionTool } from '../app_models/conversion-tool.model';

export const IMAGE_CONVERSION_TOOLS: ConversionTool[] = [
    {
        id: 'png-to-json-ai',
        title: 'AI PNG to JSON',
        description: 'Convert PNG images to JSON using AI',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-code',
        route: '/imageconversion/png-to-json-ai'
    },
    {
        id: 'jpg-to-json-ai',
        title: 'AI JPG to JSON',
        description: 'Convert JPG images to JSON using AI',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-code',
        route: '/imageconversion/jpg-to-json-ai'
    },
    {
        id: 'jpg-to-pdf',
        title: 'JPG to PDF',
        description: 'Convert JPG images to PDF format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-pdf',
        route: '/imageconversion/jpg-to-pdf'
    },
    {
        id: 'png-to-pdf',
        title: 'PNG to PDF',
        description: 'Convert PNG images to PDF format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-pdf',
        route: '/imageconversion/png-to-pdf'
    },
    {
        id: 'website-to-jpg',
        title: 'Website to JPG',
        description: 'Convert website URLs to JPG image',
        sourceIcon: 'fas fa-globe',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/website-to-jpg'
    },
    {
        id: 'html-to-jpg',
        title: 'HTML to JPG',
        description: 'Convert HTML content to JPG image',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/html-to-jpg'
    },
    {
        id: 'website-to-png',
        title: 'Website to PNG',
        description: 'Convert website URLs to PNG image',
        sourceIcon: 'fas fa-globe',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/website-to-png'
    },
    {
        id: 'html-to-png',
        title: 'HTML to PNG',
        description: 'Convert HTML content to PNG image',
        sourceIcon: 'fas fa-file-code',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/html-to-png'
    },
    {
        id: 'pdf-to-jpg',
        title: 'PDF to JPG',
        description: 'Convert PDF pages to JPG images',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/pdf-to-jpg'
    },
    {
        id: 'pdf-to-png',
        title: 'PDF to PNG',
        description: 'Convert PDF pages to PNG images',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/pdf-to-png'
    },
    {
        id: 'pdf-to-tiff',
        title: 'PDF to TIFF',
        description: 'Convert PDF pages to TIFF images',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/pdf-to-tiff'
    },
    {
        id: 'pdf-to-svg',
        title: 'PDF to SVG',
        description: 'Convert PDF pages to SVG format',
        sourceIcon: 'fas fa-file-pdf',
        targetIcon: 'fas fa-vector-square',
        route: '/imageconversion/pdf-to-svg'
    },
    {
        id: 'ai-to-svg',
        title: 'AI to SVG',
        description: 'Convert Adobe Illustrator files to SVG',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-vector-square',
        route: '/imageconversion/ai-to-svg'
    },
    {
        id: 'png-to-svg',
        title: 'PNG to SVG',
        description: 'Convert PNG images to SVG format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-vector-square',
        route: '/imageconversion/png-to-svg'
    },
    {
        id: 'png-to-avif',
        title: 'PNG to AVIF',
        description: 'Convert PNG images to AVIF format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/png-to-avif'
    },
    {
        id: 'jpg-to-avif',
        title: 'JPG to AVIF',
        description: 'Convert JPG images to AVIF format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/jpg-to-avif'
    },
    {
        id: 'webp-to-avif',
        title: 'WebP to AVIF',
        description: 'Convert WebP images to AVIF format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/webp-to-avif'
    },
    {
        id: 'avif-to-png',
        title: 'AVIF to PNG',
        description: 'Convert AVIF images to PNG format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/avif-to-png'
    },
    {
        id: 'avif-to-jpeg',
        title: 'AVIF to JPEG',
        description: 'Convert AVIF images to JPEG format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/avif-to-jpeg'
    },
    {
        id: 'avif-to-webp',
        title: 'AVIF to WebP',
        description: 'Convert AVIF images to WebP format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/avif-to-webp'
    },
    {
        id: 'png-to-webp',
        title: 'PNG to WebP',
        description: 'Convert PNG images to WebP format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/png-to-webp'
    },
    {
        id: 'jpg-to-webp',
        title: 'JPG to WebP',
        description: 'Convert JPG images to WebP format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/jpg-to-webp'
    },
    {
        id: 'tiff-to-webp',
        title: 'TIFF to WebP',
        description: 'Convert TIFF images to WebP format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/tiff-to-webp'
    },
    {
        id: 'gif-to-webp',
        title: 'GIF to WebP',
        description: 'Convert GIF images to WebP format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/gif-to-webp'
    },
    {
        id: 'webp-to-png',
        title: 'WebP to PNG',
        description: 'Convert WebP images to PNG format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/webp-to-png'
    },
    {
        id: 'webp-to-jpeg',
        title: 'WebP to JPEG',
        description: 'Convert WebP images to JPEG format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/webp-to-jpeg'
    },
    {
        id: 'webp-to-tiff',
        title: 'WebP to TIFF',
        description: 'Convert WebP images to TIFF format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/webp-to-tiff'
    },
    {
        id: 'webp-to-bmp',
        title: 'WebP to BMP',
        description: 'Convert WebP images to BMP format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/webp-to-bmp'
    },
    {
        id: 'webp-to-yuv',
        title: 'WebP to YUV',
        description: 'Convert WebP images to YUV format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/webp-to-yuv'
    },
    {
        id: 'webp-to-pam',
        title: 'WebP to PAM',
        description: 'Convert WebP images to PAM format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/webp-to-pam'
    },
    {
        id: 'webp-to-pgm',
        title: 'WebP to PGM',
        description: 'Convert WebP images to PGM format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/webp-to-pgm'
    },
    {
        id: 'webp-to-ppm',
        title: 'WebP to PPM',
        description: 'Convert WebP images to PPM format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/webp-to-ppm'
    },
    {
        id: 'png-to-jpg',
        title: 'PNG to JPG',
        description: 'Convert PNG images to JPG format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/png-to-jpg'
    },
    {
        id: 'png-to-pgm',
        title: 'PNG to PGM',
        description: 'Convert PNG images to PGM format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/png-to-pgm'
    },
    {
        id: 'png-to-ppm',
        title: 'PNG to PPM',
        description: 'Convert PNG images to PPM format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/png-to-ppm'
    },
    {
        id: 'jpg-to-png',
        title: 'JPG to PNG',
        description: 'Convert JPG images to PNG format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/jpg-to-png'
    },
    {
        id: 'jpeg-to-pgm',
        title: 'JPEG to PGM',
        description: 'Convert JPEG images to PGM format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/jpeg-to-pgm'
    },
    {
        id: 'jpeg-to-ppm',
        title: 'JPEG to PPM',
        description: 'Convert JPEG images to PPM format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/jpeg-to-ppm'
    },
    {
        id: 'heic-to-png',
        title: 'HEIC to PNG',
        description: 'Convert HEIC images to PNG format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/heic-to-png'
    },
    {
        id: 'heic-to-jpg',
        title: 'HEIC to JPG',
        description: 'Convert HEIC images to JPG format',
        sourceIcon: 'fas fa-file-image',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/heic-to-jpg'
    },
    {
        id: 'svg-to-png',
        title: 'SVG to PNG',
        description: 'Convert SVG images to PNG format',
        sourceIcon: 'fas fa-vector-square',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/svg-to-png'
    },
    {
        id: 'svg-to-jpg',
        title: 'SVG to JPG',
        description: 'Convert SVG images to JPG format',
        sourceIcon: 'fas fa-vector-square',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/svg-to-jpg'
    },
    {
        id: 'remove-exif',
        title: 'Remove EXIF',
        description: 'Remove EXIF data from images',
        sourceIcon: 'fas fa-camera',
        targetIcon: 'fas fa-file-image',
        route: '/imageconversion/remove-exif'
    }
];
