<xsl:template match="tabheader">
    <li class="{x:iif(@active or (../@active = @id), 'active', '')}">
        <a href="#{@id}" data-toggle="tab">
            <xsl:value-of select="@text" />
        </a>
    </li>
</xsl:template>

<xsl:template match="tabbody">
    <div id="{@id}" class="tab-pane {x:iif(@active or (../@active = @id), 'active', '')}">
        <xsl:apply-templates />
    </div>
</xsl:template>

<xsl:template match="tabcontrol">
    <ul id="{@id}" class="nav nav-tabs">
        <xsl:apply-templates select="./tabheader" />
    </ul>
    <div class="tab-content">
        <xsl:apply-templates select="./tabbody" />
    </div>
</xsl:template>




<xsl:template match="treecontainer">
    <div class="ui-el-treecontainernode">
        <a href="#" onclick="return Genesis.UI.toggleTreeNode('{@id}');" class="text">
            <img id="{@id}-btn" src="/dl/core/ui/tree-{x:iif(@expanded, 'minus', 'plus')}.png" />
            <xsl:value-of select="@text" />
        </a>
        <div id="{@id}" style="{x:iif(@expanded, '', 'display:none;')}">
            <xsl:apply-templates />
        </div>
    </div>
</xsl:template>

<xsl:template match="treecontainernode">
    <div class="ui-el-treecontainernode {x:iif(@active, 'active', '')}">
        <xsl:apply-templates />
    </div>
</xsl:template>


<xsl:template match="list">
    <ul class="ui-el-list" style="width: {x:css(@width, 'auto')}; height: {x:css(@height, 'auto')};">
        <xsl:apply-templates />
    </ul>
</xsl:template>

<xsl:template match="listitem">
    <li class="{x:iif(@active, 'active', '')}" onclick="return Genesis.query('/handle/listitem/click/{@id}');">
        <xsl:apply-templates />
    </li>
</xsl:template>


<xsl:template match="editable">
    <a href="#" onclick="return Genesis.UI.editableActivate('{x:idesc(@id)}')" class="ui-el-editable-inactive" id="{x:idesc(@id)}-normal">
        <xsl:value-of select="@value" />
    </a>
    <div id="{x:idesc(@id)}" class="ui-el-editable input-append" style="display:none">
        <input id="{x:idesc(@id)}-active-url" type="hidden" name="url" value="/handle/form/submit/{@id}"/>
        <input type="text" name="value" value="{@value}" />
        <hlabel class="add-on active">
            <img href="#" src="/dl/core/ui/stock/dialog-ok.png" onclick="return Genesis.submit('{x:idesc(@id)}', 'OK')" />
        </hlabel>
    </div>
</xsl:template>

<xsl:template match="editfield">
    <a href="#" onclick="return Genesis.UI.editableActivate('{x:idesc(@id)}')" class="ui-el-editable-inactive" id="{x:idesc(@id)}-normal">
        <xsl:value-of select="@value" />
    </a>
    <div id="{x:idesc(@id)}" class="ui-el-editable input-append" style="display:none">
        <input type="text" name="{x:idesc(@id)}" value="{@value}" />
    </div>
</xsl:template>

<xsl:template match="editpassword">
    <a href="#" onclick="return Genesis.UI.editableActivate(['{x:idesc(@id)}','{x:idesc(@id)}-b'])" class="ui-el-editable-inactive" id="{x:idesc(@id)}-normal">
        <xsl:value-of select="@value" />
    </a>
    <div id="{x:idesc(@id)}" class="ui-el-editable input-append" style="display:none">
        <p>Enter password twice, leave blank for no change</p>
        <input type="password" name="{x:idesc(@id)}" id="{x:idesc(@id)}-input" onkeypress="Genesis.verifyPassword('{x:idesc(@id)}-input', '{x:idesc(@id)}-b-input','password-error-message', event)" />
        <div>
            <input type="password" name="{x:idesc(@id)}b" id="{x:idesc(@id)}-b-input" onkeypress="Genesis.verifyPassword('{x:idesc(@id)}-input', '{x:idesc(@id)}-b-input', 'password-error-message', event)" style="margin-top: 15px;"/> 
        </div>
    </div>
    <!--<div id="{x:idesc(@id)}-b" class="ui-el-editable input-append" style="display: none">
        <input type="password" name="valueb" value="{@value}" id="{x:idesc(@id)}-b-input" onkeypress="Genesis.verifyPassword('{x:idesc(@id)}-input', '{x:idesc(@id)}-b-input', 'password-error-message', event)" /> 
        <hlabel class="add-on active">
        <img href="#" src="/dl/core/ui/stock/dialog-ok.png" onclick="return Genesis.submit('{x:idesc(@id)}', 'OK')" /> 
        </hlabel>
    </div>-->
    <p class="text-error" id="password-error-message" style="display:none">Passwords do not match</p>
</xsl:template>


<xsl:template match="sortlist">
    <div id="{@id}" class="ui-el-sortlist">
        <xsl:apply-templates />
    </div>
    <script>
        $('#<xsl:value-of select="@id"/>').sortable();
    </script>
</xsl:template>

<xsl:template match="sortlistitem">
    <div class="ui-el-sortlist-item{x:iif(@fixed, '-fixed', '')}" id="{@id}">
        <xsl:apply-templates />
    </div>
</xsl:template>

