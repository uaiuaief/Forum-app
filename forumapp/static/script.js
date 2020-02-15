buttons = document.querySelectorAll('.quote-btn')

buttons.forEach(function(btn) {
	btn.addEventListener('click', function(event) {
		event.preventDefault()
		showTextArea(event.target)

	})
})


function showTextArea(target){
	var xhr = new XMLHttpRequest();
	var postID = target.id.split('-')[1]; 
	var textArea = document.getElementById('body-'+postID);
	
	hidden_div = textArea.parentElement.parentElement.parentElement.parentElement;
	hidden_div.style.display = 'block';

	var route = 'http://localhost:5000/ajax/quote?post=';
	var postID = target.id.split('-')[1]; 
	var fullRoute = route+postID;
	xhr.open('GET', fullRoute, true)
	xhr.onload = function(){
		if(this.status == 200){
			textArea.value = this.responseText;
			
		}
	}
	xhr.send();
 }



