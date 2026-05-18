import { Routes } from '@angular/router';

export const AppRoutes: Routes = [
  {
    path: '',
    redirectTo: '',
    pathMatch: 'full',
  },
  {
    path: 'home',
    redirectTo: '',
    pathMatch: 'full',
  },
  {
    path: '',
    loadComponent: () => import('./app_views/home/home/home.component').then(c => c.HomeComponent)
  },
  {
    path: 'authentication',
    loadChildren: () => import('./app_views/user_management/user_authentication/user_authentication.routes').then(r => r.AuthenticatioRoutes),
  },
  {
    path: 'profile',
    loadChildren: () => import('./app_views/user_management/user_profile/user_profile.routes').then(r => r.ProfileRoutes),
  },
  {
    path: 'verification',
    loadChildren: () => import('./app_views/user_management/user_verification/user_verification.routes').then(r => r.VerificationRoutes),
  },
  {
    path: 'pdfconversion',
    loadChildren: () => import('./app_views/conversion_management/pdf_conversion/pdf_conversion.routes').then(r => r.PDFConversionRoutes),
  },
  {
    path: 'jsonconversion',
    loadChildren: () => import('./app_views/conversion_management/json_conversion/json_conversion.routes').then(r => r.JSONConversionRoutes),
  },
  {
    path: 'audioconversion',
    loadChildren: () => import('./app_views/conversion_management/audio_conversion/audio_conversion.routes').then(r => r.AudioConversionRoutes),
  },
  {
    path: 'csvconversion',
    loadChildren: () => import('./app_views/conversion_management/csv_conversion/csv_conversion.routes').then(r => r.CSVConversionRoutes),
  },
  {
    path: 'ebookconversion',
    loadChildren: () => import('./app_views/conversion_management/ebook_conversion/ebook_conversion.routes').then(r => r.EbookConversionRoutes),
  },
  {
    path: 'fileformatter',
    loadChildren: () => import('./app_views/conversion_management/file_formatter/file_formatter.routes').then(r => r.FileFormatterRoutes),
  },
  {
    path: 'imageconversion',
    loadChildren: () => import('./app_views/conversion_management/image_conversion/image_conversion.routes').then(r => r.ImageConversionRoutes),
  },
  {
    path: 'ocrconversion',
    loadChildren: () => import('./app_views/conversion_management/ocr_conversion/ocr_conversion.routes').then(r => r.OCRConversionRoutes),
  },
  {
    path: 'officeconversion',
    loadChildren: () => import('./app_views/conversion_management/office_conversion/office_conversion.routes').then(r => r.OfficeConversionRoutes),
  },
  {
    path: 'subtitleconversion',
    loadChildren: () => import('./app_views/conversion_management/subtitle_conversion/subtitle_conversion.routes').then(r => r.SubtitleConversionRoutes),
  },
  {
    path: 'textconversion',
    loadChildren: () => import('./app_views/conversion_management/text_conversion/text_conversion.routes').then(r => r.TextConversionRoutes),
  },
  {
    path: 'markdownconversion',
    loadChildren: () => import('./app_views/conversion_management/markdown_conversion/markdown_conversion.routes').then(r => r.MARKDOWN_CONVERSION_ROUTES),
  },
  {
    path: 'videoconversion',
    loadChildren: () => import('./app_views/conversion_management/video_conversion/video_conversion.routes').then(r => r.VideoConversionRoutes),
  },
  {
    path: 'websiteconversion',
    loadChildren: () => import('./app_views/conversion_management/website_conversion/website_conversion.routes').then(r => r.WebsiteConversionRoutes),
  },
  {
    path: 'xmlconversion',
    loadChildren: () => import('./app_views/conversion_management/xml_conversion/xml_conversion.routes').then(r => r.XMLConversionRoutes),
  },
  {
    path: 'privacy-policy',
    loadComponent: () => import('./app_views/privacy_policy/privacy_policy.component').then(c => c.PrivacyPolicyComponent)
  },
  {
    path: 'terms-of-service',
    loadComponent: () => import('./app_views/terms_of_service/terms_of_service.component').then(c => c.TermsOfServiceComponent)
  },
  {
    path: 'about-us',
    loadComponent: () => import('./app_views/about_us/about_us.component').then(c => c.AboutUsComponent)
  },
  {
    path: 'contact-us',
    loadComponent: () => import('./app_views/contact_us/contact_us.component').then(c => c.ContactUsComponent)
  },
  {
    path: 'pricing',
    loadComponent: () => import('./app_views/pricing/pricing.component').then(c => c.PricingComponent)
  },
  {
    path: 'subscription/success',
    loadComponent: () => import('./app_views/subscription/subscription-success.component').then(c => c.SubscriptionSuccessComponent)
  },
  {
    path: 'subscription/cancel',
    loadComponent: () => import('./app_views/subscription/subscription-cancel.component').then(c => c.SubscriptionCancelComponent)
  },
  {
    path: 'tools',
    loadComponent: () => import('./app_views/conversion_management/tools-category/tools-category.component').then(c => c.ToolsCategoryComponent)
  },
  {
    path: 'helpdesk',
    loadChildren: () => import('./app_views/helpdesk_management/helpdesk_management.routes').then(r => r.HelpdeskManagementRoutes)
  },
  {
    path: '**',
    loadComponent: () => import('./app_views/not_found/not_found.component').then(c => c.NotFoundComponent)
  }
];
