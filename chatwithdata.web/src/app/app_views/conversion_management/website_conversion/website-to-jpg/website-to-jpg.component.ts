import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseWebsiteToolComponent } from '../base-website-tool.component';

@Component({
  selector: 'app-website-to-jpg',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './website-to-jpg.component.html',
  styleUrl: './website-to-jpg.component.css',
  standalone: true
})
export class WebsiteToJpgComponent extends BaseWebsiteToolComponent {
  toolId = 'website-to-jpg';
}
