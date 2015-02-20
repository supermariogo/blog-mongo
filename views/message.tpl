%include('header.tpl', html_title='Message')
%include('nav.tpl')


<body>

  <div class="container">
    <div class="row">
      <div class="col-md-3">
        %include('userhome_sidenavbar_template.tpl')
      </div>
      <div class="col-md-9">
        <div class="panel panel-default">
          <div class="panel-heading">Message</div>
          <div class="panel-body">
            %include('message_compose.tpl')
            %include('message_list.tpl', is_group=0)
          </div>
        </div>
      </div>
    </div>
  </div>


</body>

%include('footer.tpl')
