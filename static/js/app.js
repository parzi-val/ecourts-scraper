class ECourtsApp {
    constructor() {
        this.currentStep = 1;
        this.states = [];
        this.districts = [];
        this.selectedState = null;
        this.selectedDistrict = null;
        this.courtComplexes = {};
        this.caseTypes = {};
        this.selectedCourtComplex = null;
        this.selectedCaseType = null;
        this.caseNumber = null;
        this.caseYear = null;
        this.captchaValue = null;

        this.initializeEventListeners();
        this.loadStates(); // Load states on app start
    }

    async loadStates() {
        try {
            const response = await axios.get('/api/states');
            if (response.data.success) {
                this.states = response.data.states;
                const stateSelect = document.getElementById('state-select');
                stateSelect.innerHTML = '<option value="">Select a state...</option>';
                this.states.forEach(state => {
                    const option = document.createElement('option');
                    option.value = state;
                    option.textContent = state;
                    stateSelect.appendChild(option);
                });
            } else {
                this.showMessage('Failed to load states', 'error');
            }
        } catch (error) {
            this.showMessage('Failed to load states', 'error');
            console.error('Error:', error);
        }
    }

    async loadDistricts() {
        try {
            const response = await axios.post('/api/districts', {
                state: this.selectedState
            });
            if (response.data.success) {
                this.districts = response.data.districts;
                const districtSelect = document.getElementById('district-select');
                districtSelect.innerHTML = '<option value="">Select a district...</option>';
                this.districts.forEach(district => {
                    const option = document.createElement('option');
                    option.value = district;
                    option.textContent = district;
                    districtSelect.appendChild(option);
                });
                districtSelect.disabled = false;
                this.goToStep(2);
            } else {
                this.showMessage('Failed to load districts', 'error');
            }
        } catch (error) {
            this.showMessage('Failed to load districts', 'error');
            console.error('Error:', error);
        }
    }

    initializeEventListeners() {
        // State selection
        document.getElementById('state-select').addEventListener('change', (e) => {
            this.selectedState = e.target.value;
            document.getElementById('next-step-1').disabled = !this.selectedState;
        });

        // District selection
        document.getElementById('district-select').addEventListener('change', (e) => {
            this.selectedDistrict = e.target.value;
            document.getElementById('next-step-2').disabled = !this.selectedDistrict;
        });

        // Initialize session button
        document.getElementById('init-btn').addEventListener('click', () => {
            this.initializeSession();
        });

        // Court complex selection
        document.getElementById('court-complex-select').addEventListener('change', (e) => {
            this.selectedCourtComplex = e.target.value;
            document.getElementById('next-step-4').disabled = !this.selectedCourtComplex;
        });

        // Case type selection
        document.getElementById('case-type-select').addEventListener('change', (e) => {
            this.selectedCaseType = e.target.value;
            document.getElementById('next-step-5').disabled = !this.selectedCaseType;
        });

        // Navigation buttons
        document.getElementById('next-step-1').addEventListener('click', () => {
            this.loadDistricts();
        });

        document.getElementById('next-step-2').addEventListener('click', () => {
            this.goToStep(3);
        });

        document.getElementById('next-step-4').addEventListener('click', () => {
            this.loadCaseTypes();
        });

        document.getElementById('next-step-5').addEventListener('click', () => {
            this.goToStep(6);
        });

        document.getElementById('next-step-6').addEventListener('click', () => {
            this.caseNumber = document.getElementById('case-number').value;
            this.caseYear = document.getElementById('case-year').value;
            if (this.caseNumber && this.caseYear) {
                this.goToStep(7);
            } else {
                alert('Please enter both case number and year');
            }
        });

        document.getElementById('next-step-7').addEventListener('click', () => {
            this.captchaValue = document.getElementById('captcha-input').value;
            if (this.captchaValue) {
                this.searchCase();
            } else {
                alert('Please enter the CAPTCHA text');
            }
        });

        // Previous buttons
        document.getElementById('prev-step-2').addEventListener('click', () => {
            this.goToStep(1);
        });

        document.getElementById('prev-step-3').addEventListener('click', () => {
            this.goToStep(2);
        });

        document.getElementById('prev-step-5').addEventListener('click', () => {
            this.goToStep(4);
        });

        document.getElementById('prev-step-6').addEventListener('click', () => {
            this.goToStep(5);
        });

        document.getElementById('prev-step-7').addEventListener('click', () => {
            this.goToStep(6);
        });

        // CAPTCHA refresh
        document.getElementById('refresh-captcha').addEventListener('click', () => {
            this.loadCaptcha();
        });

        // New search
        document.getElementById('new-search').addEventListener('click', () => {
            this.resetApp();
        });
    }

    async initializeSession() {
        const initBtn = document.getElementById('init-btn');
        const originalText = initBtn.innerHTML;

        initBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Initializing...';
        initBtn.disabled = true;

        try {
            const response = await axios.post('/api/initialize', {
                state: this.selectedState,
                district: this.selectedDistrict
            });

            if (response.data.success) {
                this.updateStepStatus(3, 'completed');
                this.goToStep(4);
                this.loadCourtComplexes();
            } else {
                alert('Failed to initialize session: ' + response.data.message);
            }
        } catch (error) {
            console.error('Error initializing session:', error);
            alert('Error initializing session. Please try again.');
        } finally {
            initBtn.innerHTML = originalText;
            initBtn.disabled = false;
        }
    }

    async loadCourtComplexes() {
        try {
            const response = await axios.get('/api/court-complexes');

            if (response.data.success) {
                this.courtComplexes = response.data.court_complexes;
                this.populateCourtComplexSelect();
            } else {
                alert('Failed to load court complexes');
            }
        } catch (error) {
            console.error('Error loading court complexes:', error);
            alert('Error loading court complexes. Please try again.');
        }
    }

    populateCourtComplexSelect() {
        const select = document.getElementById('court-complex-select');
        select.innerHTML = '<option value="">Select a court complex...</option>';

        for (const [name, code] of Object.entries(this.courtComplexes)) {
            const option = document.createElement('option');
            option.value = code;
            option.textContent = name;
            select.appendChild(option);
        }

        select.disabled = false;
    }

    async loadCaseTypes() {
        if (!this.selectedCourtComplex) {
            alert('Please select a court complex first');
            return;
        }

        const nextBtn = document.getElementById('next-step-4');
        const originalText = nextBtn.innerHTML;

        nextBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Loading...';
        nextBtn.disabled = true;

        try {
            const response = await axios.post('/api/case-types', {
                court_complex_code: this.selectedCourtComplex
            });

            if (response.data.success) {
                this.caseTypes = response.data.case_types;
                this.populateCaseTypeSelect();
                this.updateStepStatus(4, 'completed');
                this.goToStep(5);
            } else {
                alert('Failed to load case types: ' + response.data.message);
            }
        } catch (error) {
            console.error('Error loading case types:', error);
            alert('Error loading case types. Please try again.');
        } finally {
            nextBtn.innerHTML = originalText;
            nextBtn.disabled = false;
        }
    }

    populateCaseTypeSelect() {
        const select = document.getElementById('case-type-select');
        select.innerHTML = '<option value="">Select a case type...</option>';

        for (const [name, code] of Object.entries(this.caseTypes)) {
            const option = document.createElement('option');
            option.value = code;
            option.textContent = name;
            select.appendChild(option);
        }

        select.disabled = false;
    }

    async loadCaptcha() {
        const refreshBtn = document.getElementById('refresh-captcha');
        const originalText = refreshBtn.innerHTML;

        refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Loading...';
        refreshBtn.disabled = true;

        try {
            const response = await axios.get('/api/captcha');

            if (response.data.success) {
                const captchaImg = document.getElementById('captcha-image');
                captchaImg.src = response.data.captcha_image;
                captchaImg.style.display = 'block';
                refreshBtn.innerHTML = '<i class="fas fa-refresh mr-2"></i>Refresh CAPTCHA';
            } else {
                alert('Failed to load CAPTCHA: ' + response.data.message);
            }
        } catch (error) {
            console.error('Error loading CAPTCHA:', error);
            alert('Error loading CAPTCHA. Please try again.');
        } finally {
            refreshBtn.disabled = false;
        }
    }

    async searchCase() {
        const searchBtn = document.getElementById('next-step-7');
        const originalText = searchBtn.innerHTML;

        searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Searching...';
        searchBtn.disabled = true;

        this.updateStepStatus(7, 'completed');
        this.goToStep(8);

        // Show loading in results
        document.getElementById('loading-results').style.display = 'block';
        document.getElementById('results-container').innerHTML = '';

        try {
            const response = await axios.post('/api/search', {
                state: this.selectedState,
                district: this.selectedDistrict,
                court_complex: this.selectedCourtComplex,
                case_type: this.selectedCaseType,
                case_number: this.caseNumber,
                year: this.caseYear,
                captcha_value: this.captchaValue
            });

            document.getElementById('loading-results').style.display = 'none';

            if (response.data.success) {
                this.displayResults(response.data.case_details);
                this.updateStepStatus(7, 'completed');
            } else {
                this.displayError(response.data.message);
            }
        } catch (error) {
            console.error('Error searching case:', error);
            document.getElementById('loading-results').style.display = 'none';
            this.displayError('Error searching for case. Please try again.');
        } finally {
            searchBtn.innerHTML = originalText;
            searchBtn.disabled = false;
        }
    }

    displayResults(caseDetails) {
        const container = document.getElementById('results-container');

        // Debug: Log the case details to console
        console.log('Case Details received:', caseDetails);

        let html = `
            <div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                <h3 class="text-lg font-semibold text-green-800 mb-2">
                    <i class="fas fa-check-circle mr-2"></i>Case Found Successfully
                </h3>
            </div>
        `;

        // Case Details
        if (caseDetails.case_type || caseDetails.filing_number || caseDetails.registration_number) {
            html += `
                <div class="bg-white border border-gray-200 rounded-lg p-4">
                    <h4 class="font-semibold text-gray-800 mb-3">Case Details</h4>
                    <div class="grid grid-cols-2 gap-4 text-sm">
                        ${caseDetails.case_type ? `<div><span class="font-medium">Case Type:</span> ${caseDetails.case_type}</div>` : ''}
                        ${caseDetails.filing_number ? `<div><span class="font-medium">Filing Number:</span> ${caseDetails.filing_number}</div>` : ''}
                        ${caseDetails.filing_date ? `<div><span class="font-medium">Filing Date:</span> ${caseDetails.filing_date}</div>` : ''}
                        ${caseDetails.registration_number ? `<div><span class="font-medium">Registration Number:</span> ${caseDetails.registration_number}</div>` : ''}
                        ${caseDetails.registration_date ? `<div><span class="font-medium">Registration Date:</span> ${caseDetails.registration_date}</div>` : ''}
                        ${caseDetails.cnr_number ? `<div><span class="font-medium">CNR Number:</span> ${caseDetails.cnr_number}</div>` : ''}
                    </div>
                </div>
            `;
        }

        // Case Status
        if (caseDetails.case_status || caseDetails.decision_date) {
            html += `
                <div class="bg-white border border-gray-200 rounded-lg p-4">
                    <h4 class="font-semibold text-gray-800 mb-3">Case Status</h4>
                    <div class="grid grid-cols-2 gap-4 text-sm">
                        ${caseDetails.first_hearing_date ? `<div><span class="font-medium">First Hearing:</span> ${caseDetails.first_hearing_date}</div>` : ''}
                        ${caseDetails.decision_date ? `<div><span class="font-medium">Decision Date:</span> ${caseDetails.decision_date}</div>` : ''}
                        ${caseDetails.case_status ? `<div><span class="font-medium">Status:</span> ${caseDetails.case_status}</div>` : ''}
                        ${caseDetails.nature_of_disposal ? `<div><span class="font-medium">Nature of Disposal:</span> ${caseDetails.nature_of_disposal}</div>` : ''}
                        ${caseDetails.court_number_and_judge ? `<div><span class="font-medium">Court & Judge:</span> ${caseDetails.court_number_and_judge}</div>` : ''}
                    </div>
                </div>
            `;
        }

        // FIR Details
        if (caseDetails.police_station || caseDetails.fir_number) {
            html += `
                <div class="bg-white border border-gray-200 rounded-lg p-4">
                    <h4 class="font-semibold text-gray-800 mb-3">FIR Details</h4>
                    <div class="grid grid-cols-2 gap-4 text-sm">
                        ${caseDetails.police_station ? `<div><span class="font-medium">Police Station:</span> ${caseDetails.police_station}</div>` : ''}
                        ${caseDetails.fir_number ? `<div><span class="font-medium">FIR Number:</span> ${caseDetails.fir_number}</div>` : ''}
                        ${caseDetails.fir_year ? `<div><span class="font-medium">FIR Year:</span> ${caseDetails.fir_year}</div>` : ''}
                    </div>
                </div>
            `;
        }

        // Petitioners
        if (caseDetails.petitioners && caseDetails.petitioners.length > 0) {
            html += `
                <div class="bg-white border border-gray-200 rounded-lg p-4">
                    <h4 class="font-semibold text-gray-800 mb-3">Petitioners</h4>
                    <ul class="list-disc list-inside text-sm">
                        ${caseDetails.petitioners.map((petitioner, index) => `<li>${index + 1}) ${petitioner}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        // Respondents
        if (caseDetails.respondents && caseDetails.respondents.length > 0) {
            html += `
                <div class="bg-white border border-gray-200 rounded-lg p-4">
                    <h4 class="font-semibold text-gray-800 mb-3">Respondents</h4>
                    <ul class="list-disc list-inside text-sm">
                        ${caseDetails.respondents.map((respondent, index) => `<li>${index + 1}) ${respondent}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        // Case History
        if (caseDetails.case_history && caseDetails.case_history.length > 0) {
            html += `
                 <div class="bg-white border border-gray-200 rounded-lg p-4">
                     <h4 class="font-semibold text-gray-800 mb-3">Case History</h4>
                     <div class="space-y-2">
                         ${caseDetails.case_history.map((entry, index) => `
                             <div class="border-l-4 border-blue-500 pl-3 py-2">
                                 <div class="text-sm">
                                     <span class="font-medium">Entry ${index + 1}:</span>
                                     ${entry.registration_number ? `Reg: ${entry.registration_number}` : ''}
                                     ${entry.judge ? ` | Judge: ${entry.judge}` : ''}
                                     ${entry.business_date ? ` | Business Date: ${entry.business_date}` : ''}
                                     ${entry.hearing_date ? ` | Hearing Date: ${entry.hearing_date}` : ''}
                                     ${entry.purpose ? ` | Purpose: ${entry.purpose}` : ''}
                                 </div>
                             </div>
                         `).join('')}
                     </div>
                 </div>
             `;
        }

        // Acts - NEW SECTION FOR ONGOING CASES
        console.log('Checking acts:', caseDetails.acts);
        if (caseDetails.acts && caseDetails.acts.length > 0) {
            console.log('Adding acts section');
            html += `
                 <div class="bg-white border border-gray-200 rounded-lg p-4">
                     <h4 class="font-semibold text-gray-800 mb-3">Acts</h4>
                     <div class="space-y-2">
                         ${caseDetails.acts.map((act, index) => `
                             <div class="border-l-4 border-green-500 pl-3 py-2">
                                 <div class="text-sm">
                                     <span class="font-medium">Act ${index + 1}:</span>
                                     ${act.under_act ? `Under Act: ${act.under_act}` : ''}
                                     ${act.under_section ? ` | Section: ${act.under_section}` : ''}
                                 </div>
                             </div>
                         `).join('')}
                     </div>
                 </div>
             `;
        }

        // Orders - NEW SECTION FOR ONGOING CASES (WITH DOWNLOAD LINKS)
        console.log('Checking orders:', caseDetails.orders);
        if (caseDetails.orders && caseDetails.orders.length > 0) {
            console.log('Adding orders section');
            html += `
                 <div class="bg-white border border-gray-200 rounded-lg p-4">
                     <h4 class="font-semibold text-gray-800 mb-3">Orders</h4>
                     <div class="space-y-2">
                         ${caseDetails.orders.map((order, index) => `
                             <div class="border-l-4 border-purple-500 pl-3 py-2">
                                 <div class="text-sm">
                                     <span class="font-medium">Order ${index + 1}:</span>
                                     ${order.order_number ? `Number: ${order.order_number}` : ''}
                                     ${order.order_date ? ` | Date: ${order.order_date}` : ''}
                                     ${order.order_details ? ` | Details: ${order.order_details}` : ''}
                                     ${order.download_link ? `
                                         <div class="mt-1">
                                             <a href="${order.download_link}" target="_blank" 
                                                class="text-blue-600 hover:text-blue-800 underline text-xs">
                                                 <i class="fas fa-download mr-1"></i>Download Order
                                             </a>
                                         </div>
                                     ` : ''}
                                 </div>
                             </div>
                         `).join('')}
                     </div>
                 </div>
             `;
        }

        // Process Details - NEW SECTION FOR ONGOING CASES
        console.log('Checking process_details:', caseDetails.process_details);
        if (caseDetails.process_details && caseDetails.process_details.length > 0) {
            console.log('Adding process details section');
            html += `
                 <div class="bg-white border border-gray-200 rounded-lg p-4">
                     <h4 class="font-semibold text-gray-800 mb-3">Process Details</h4>
                     <div class="space-y-2">
                         ${caseDetails.process_details.map((process, index) => `
                             <div class="border-l-4 border-orange-500 pl-3 py-2">
                                 <div class="text-sm">
                                     <span class="font-medium">Process ${index + 1}:</span>
                                     ${process.process_id ? `ID: ${process.process_id}` : ''}
                                     ${process.process_date ? ` | Date: ${process.process_date}` : ''}
                                     ${process.process_title ? ` | Title: ${process.process_title}` : ''}
                                     ${process.party_name ? ` | Party: ${process.party_name}` : ''}
                                     ${process.issued_process ? ` | Issued: ${process.issued_process}` : ''}
                                 </div>
                             </div>
                         `).join('')}
                     </div>
                 </div>
             `;
        }

        container.innerHTML = html;
    }

    displayError(message) {
        const container = document.getElementById('results-container');
        container.innerHTML = `
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                <h3 class="text-lg font-semibold text-red-800 mb-2">
                    <i class="fas fa-exclamation-circle mr-2"></i>Search Failed
                </h3>
                <p class="text-red-700">${message}</p>
            </div>
        `;
    }

    goToStep(step) {
        // Hide all steps
        document.querySelectorAll('.form-step').forEach(el => {
            el.classList.remove('active');
        });

        // Show current step
        document.getElementById(`step-${step}`).classList.add('active');

        // Update progress
        this.updateStepStatus(step, 'active');

        // Load CAPTCHA if it's step 7
        if (step === 7) {
            this.loadCaptcha();
        }

        this.currentStep = step;
    }

    updateStepStatus(step, status) {
        const stepElement = document.querySelector(`[data-step="${step}"]`);

        // Check if the step element exists (for steps that don't have sidebar items)
        if (!stepElement) {
            console.log(`Step ${step} doesn't have a sidebar item, skipping status update`);
            return;
        }

        const circle = stepElement.querySelector('.step-circle');

        // Remove all status classes
        circle.classList.remove('step-active', 'step-completed', 'step-pending');

        // Add appropriate status class
        circle.classList.add(`step-${status}`);

        // Update icon based on status
        if (status === 'completed') {
            circle.innerHTML = '<i class="fas fa-check"></i>';
        } else if (status === 'active') {
            // Keep original icon for active state
        }
    }

    resetApp() {
        // Reset all form fields
        document.getElementById('state-select').value = '';
        document.getElementById('district-select').value = '';
        document.getElementById('district-select').disabled = true;
        document.getElementById('court-complex-select').value = '';
        document.getElementById('case-type-select').value = '';
        document.getElementById('case-number').value = '';
        document.getElementById('case-year').value = '';
        document.getElementById('captcha-input').value = '';
        document.getElementById('captcha-image').style.display = 'none';

        // Reset step status
        for (let i = 1; i <= 7; i++) {
            this.updateStepStatus(i, 'pending');
        }

        // Reset data
        this.selectedState = null;
        this.selectedDistrict = null;
        this.selectedCourtComplex = null;
        this.selectedCaseType = null;
        this.caseNumber = null;
        this.caseYear = null;
        this.captchaValue = null;

        // Go back to step 1 and reload states
        this.goToStep(1);
        this.loadStates();
    }
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ECourtsApp();
}); 