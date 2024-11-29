import { Component } from '@angular/core';
import { RouterOutlet, ActivatedRoute } from '@angular/router';
import { DataService } from './data.service';


@Component({
selector: 'singleJob',
standalone: true,
imports: [RouterOutlet],
providers: [DataService],
templateUrl: './singleJob.component.html',
styleUrl: './singleJob.component.css'
})
export class singleJobComponent {
    singlejob_list: any;
    constructor( public dataService: DataService,
        private route: ActivatedRoute) {}
    ngOnInit() {
        this.singlejob_list =
            this.dataService.getjob(
                this.route.snapshot.paramMap.get('id'));
    
        }
}