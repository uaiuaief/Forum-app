$(document).ready(function(){
	$('.post').click(function(e){
		var id = this.id;
		if($(e.target).hasClass('quote-btn')){
			e.preventDefault();
			$('.reply-box-'+id).toggle();
			var quote_text = $('#'+id+' div.post-content p').text();
			$('textarea#body-'+id).val('<quote>'+quote_text+'</quote>');
		}
	});
	
	var $userInput = $('.fields input[name="user"]');
	var $passwordInput = $('.fields input[name="password"]');

	$(document).mousedown(function(event){
		$target = $(event.target);
		
		if ($target.attr('name') != 'user' && $userInput.val() == '' ){
			$userInput.val('Username');
			$userInput.css('color', '#999');
		};

		if ($target.attr('name') != 'password' && $passwordInput.val() == ''){
			$passwordInput.val('Password');
			$passwordInput.attr('type', 'text');
			$passwordInput.css('color', '#999');
		};
	});


	$userInput.focus(function(){
		if($userInput.css('color') == 'rgb(153, 153, 153)'){
			$(this).val('');
			$(this).css('color', 'black');
		};
	});

	$passwordInput.focus(function(){
		if($passwordInput.attr('type') == 'text'){
			$(this).attr('type', 'password');
			$(this).css('color', 'black');
			$(this).val('');
		};
	});

	$('#login-form').submit(function(e){
		e.preventDefault();
		var $userInput = $('.fields input[name="user"]');
		var $passwordInput = $('.fields input[name="password"]');
		var url = $(this).attr('action');

		$.post(url, {username:$userInput, password:$passwordInput}).
			done(function(data){
				console.log('Login');
			});
	})









});







/*
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

*/

