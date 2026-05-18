import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseWebsiteToolComponent } from '../base-website-tool.component';

@Component({
  selector: 'app-website-to-png',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './website-to-png.component.html',
  styleUrl: './website-to-png.component.css',
  standalone: true
})
export class WebsiteToPngComponent extends BaseWebsiteToolComponent {
  toolId = 'website-to-png';
}
