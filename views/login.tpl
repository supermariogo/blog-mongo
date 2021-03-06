%include('header.tpl', html_title='登录')
<!-- Custom styles for this template -->
<link href="/static/css/signin.css" rel="stylesheet">

<body>

  <div class="container">

    <form class="form-signin" method="post" action="/login">
      %if (verify != ""):
      <div class="alert alert-success" role="alert">{{verify}}</div>
      %end
      <h2 class="form-signin-heading">Sign in</h2>
      <label for="inputEmail" class="sr-only">Email address</label>
      <input type="email" id="inputEmail" class="form-control" placeholder="Email address" name="email" value="{{email}}" required autofocus>
      <label for="inputPassword" class="sr-only">Password</label>
      <input type="password" id="inputPassword" class="form-control" placeholder="Password" name="password" required>
      <div class="checkbox">
        <label>
          <input type="checkbox" value="remember-me"> Remember me
        </label>
      </div>
      <div>
        <a href="/forget"> Forget Password?</a>
        <a class="pull-right" href="/signup">Sign Up<p></a>
      </div>
      %if (errors != ""):
      <div class="alert alert-danger" role="alert">{{errors}}</div>
      %end
      <button class="btn btn-lg btn-primary btn-block" type="submit">Sign in</button>
    </form>

  </div> <!-- /container -->
</body>

%include('footer.tpl')
