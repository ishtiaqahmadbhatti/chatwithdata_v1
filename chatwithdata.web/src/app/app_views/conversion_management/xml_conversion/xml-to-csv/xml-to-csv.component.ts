import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseXmlToolComponent } from '../base-xml-tool.component';

@Component({
  selector: 'app-xml-to-csv',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './xml-to-csv.component.html',
  styleUrl: './xml-to-csv.component.css',
  standalone: true
})
export class XmlToCsvComponent extends BaseXmlToolComponent {
  toolId = 'xml-to-csv';
}
