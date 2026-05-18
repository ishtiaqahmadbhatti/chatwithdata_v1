import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseXmlToolComponent } from '../base-xml-tool.component';

@Component({
  selector: 'app-csv-to-xml',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './csv-to-xml.component.html',
  styleUrl: './csv-to-xml.component.css',
  standalone: true
})
export class CsvToXmlComponent extends BaseXmlToolComponent {
  toolId = 'csv-to-xml';
}
