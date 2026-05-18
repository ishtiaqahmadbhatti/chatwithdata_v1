import { Routes } from '@angular/router';

export const PDFConversionRoutes: Routes = [
  {
    path: '',
    loadComponent: () => import('./pdf-conversion.component').then(c => c.PdfConversionComponent)
  },
  {
    path: 'pdf-to-word',
    loadComponent: () => import('./pdf-to-word/pdf-to-word.component').then(c => c.PdfToWordComponent)
  },
  {
    path: 'pdf-to-json',
    loadComponent: () => import('./pdf-to-json/pdf-to-json.component').then(c => c.PdfToJsonComponent)
  },
  {
    path: 'pdf-to-markdown',
    loadComponent: () => import('./pdf-to-markdown/pdf-to-markdown.component').then(c => c.PdfToMarkdownComponent)
  },
  {
    path: 'html-to-pdf',
    loadComponent: () => import('./html-to-pdf/html-to-pdf.component').then(c => c.HtmlToPdfComponent)
  },
  {
    path: 'word-to-pdf',
    loadComponent: () => import('./word-to-pdf/word-to-pdf.component').then(c => c.WordToPdfComponent)
  },
  {
    path: 'powerpoint-to-pdf',
    loadComponent: () => import('./powerpoint-to-pdf/powerpoint-to-pdf.component').then(c => c.PowerpointToPdfComponent)
  },
  {
    path: 'oxps-to-pdf',
    loadComponent: () => import('./oxps-to-pdf/oxps-to-pdf.component').then(c => c.OxpsToPdfComponent)
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
    path: 'markdown-to-pdf',
    loadComponent: () => import('./markdown-to-pdf/markdown-to-pdf.component').then(c => c.MarkdownToPdfComponent)
  },
  {
    path: 'excel-to-pdf',
    loadComponent: () => import('./excel-to-pdf/excel-to-pdf.component').then(c => c.ExcelToPdfComponent)
  },
  {
    path: 'ods-to-pdf',
    loadComponent: () => import('./ods-to-pdf/ods-to-pdf.component').then(c => c.OdsToPdfComponent)
  },
  {
    path: 'pdf-to-csv',
    loadComponent: () => import('./pdf-to-csv/pdf-to-csv.component').then(c => c.PdfToCsvComponent)
  },
  {
    path: 'pdf-to-excel',
    loadComponent: () => import('./pdf-to-excel/pdf-to-excel.component').then(c => c.PdfToExcelComponent)
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
    path: 'pdf-to-html',
    loadComponent: () => import('./pdf-to-html/pdf-to-html.component').then(c => c.PdfToHtmlComponent)
  },
  {
    path: 'pdf-to-text',
    loadComponent: () => import('./pdf-to-text/pdf-to-text.component').then(c => c.PdfToTextComponent)
  },
  {
    path: 'merge',
    loadComponent: () => import('./merge/merge.component').then(c => c.MergeComponent)
  },
  {
    path: 'split',
    loadComponent: () => import('./split/split.component').then(c => c.SplitComponent)
  },
  {
    path: 'compress',
    loadComponent: () => import('./compress/compress.component').then(c => c.CompressComponent)
  },
  {
    path: 'remove-pages',
    loadComponent: () => import('./remove-pages/remove-pages.component').then(c => c.RemovePagesComponent)
  },
  {
    path: 'extract-pages',
    loadComponent: () => import('./extract-pages/extract-pages.component').then(c => c.ExtractPagesComponent)
  },
  {
    path: 'rotate',
    loadComponent: () => import('./rotate/rotate.component').then(c => c.RotateComponent)
  },
  {
    path: 'add-watermark',
    loadComponent: () => import('./add-watermark/add-watermark.component').then(c => c.AddWatermarkComponent)
  },
  {
    path: 'add-page-numbers',
    loadComponent: () => import('./add-page-numbers/add-page-numbers.component').then(c => c.AddPageNumbersComponent)
  },
  {
    path: 'crop',
    loadComponent: () => import('./crop/crop.component').then(c => c.CropComponent)
  },
  {
    path: 'protect',
    loadComponent: () => import('./protect/protect.component').then(c => c.ProtectComponent)
  },
  {
    path: 'unlock',
    loadComponent: () => import('./unlock/unlock.component').then(c => c.UnlockComponent)
  },
  {
    path: 'repair',
    loadComponent: () => import('./repair/repair.component').then(c => c.RepairComponent)
  },
  {
    path: 'compare',
    loadComponent: () => import('./compare/compare.component').then(c => c.CompareComponent)
  },
  {
    path: 'metadata',
    loadComponent: () => import('./metadata/metadata.component').then(c => c.MetadataComponent)
  }
];
